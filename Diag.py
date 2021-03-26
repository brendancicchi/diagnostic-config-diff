import click
import glob
import os
import requests

from colorama import Fore
from colorama import Style
from parsers.ParseNTStatus import NTStatusObject
from differs.DiffYamlDict import DiffYamlDict
from differs.DiffNTVersion import DiffNTVersion
from utils import utils

cassandra_always_unique_keys = ["rpc_address", "broadcast_rpc_address", "listen_address", \
    "broadcast_address", "native_transport_address", "native_transport_broadcast_address", \
    "initial_token"]
cassandra_data_directories = ["hints_directory", "data_file_directories", \
    "saved_caches_directory", "commitlog_directory"]
dse_data_directories = ["solr_data_dir", "dsefs_options.data_directories.dir", \
    "dsefs_options.work_dir", "insights_options.data_dir"]
jvm_always_unique_keys = [
  '-Dmx4jaddress',
  '-Djava.rmi.server.hostname',
  '-javaagent:/home/automaton/jolokia-jvm-agent.jar'
]
wildcard_path = 'nodes/*'
cassandra_yaml_path = 'conf/cassandra/cassandra.yaml'
dse_yaml_path = 'conf/dse/dse.yaml'
jvm_cmdline_path = 'java_command_line.txt'
os_info_path = 'os-info.txt'
nodetool_status_path = 'nodetool/status'
nodetool_version_path = 'nodetool/version'

class Diag():
  def __init__(self, diag_path, group_by_dc=False):
    self.diag_path = os.path.abspath(diag_path)
    full_wildcard_path = os.path.join(self.diag_path, wildcard_path)
    self.group_by_dc = group_by_dc
    self.ntStatus = self.__get_nodetool_status(full_wildcard_path)
    self.ips_by_dc_dict = self.__group_paths_by_dc(full_wildcard_path) #dict
    self.all_ips_list = glob.glob(full_wildcard_path) #list
    self.version = None
      
  def diff(self, all=False, cassandra=True, include_default=False, dse=False, version=False, exclude_data_dirs=False):
    self.__print_header()
    if all or version:
      self.__version_diff(version or all)
    if all or cassandra:
      if exclude_data_dirs:
        cassandra_always_unique_keys.extend(cassandra_data_directories)
      self.__yaml_diff(cassandra_yaml_path, cassandra_always_unique_keys)
    if all or dse:
      if exclude_data_dirs:
        self.__yaml_diff(dse_yaml_path, dse_data_directories)
      else:
        self.__yaml_diff(dse_yaml_path)
  
  def __version_diff(self, check_print):
    versionDiff = DiffNTVersion(
      map(lambda base: os.path.join(base, nodetool_version_path), self.all_ips_list)
    )
    self.version = versionDiff.get_version()
    if check_print:
      version_message = ""
      if versionDiff.get_version() != None:
        version_message = " :: {0}".format(self.version)
      self.__print_sub_header("Cassandra Version{0}".format(version_message))
      self.__print_diff(versionDiff)

  def __yaml_diff(self, yaml_path, unique_keys=[]):
    if self.group_by_dc:
      for dc, ip_list in self.ips_by_dc_dict.items():
        self.__print_sub_header("{0} :: {1}".format(dc, utils.get_path_segment_from_end(yaml_path, 1)))
        yamlDiff = DiffYamlDict(
          (map(lambda base: os.path.join(base, yaml_path), ip_list)),
          unique_keys
        )
        self.__print_diff(yamlDiff)
    else:
      self.__print_sub_header("{0}".format(utils.get_path_segment_from_end(yaml_path, 1)))
      yamlDiff = DiffYamlDict(
        map(lambda base: os.path.join(base, yaml_path), self.all_ips_list),
        unique_keys
      )
      self.__print_diff(yamlDiff)

  def __group_paths_by_dc(self, wildcard_path):
    dc_paths = dict()
    for dc in self.ntStatus.dc_to_ip_map.keys():
      paths = []
      for ip in self.ntStatus.dc_to_ip_map[dc]:
        paths.append(wildcard_path.replace("*", ip))
      dc_paths[dc] = paths
    return dc_paths

  def __get_nodetool_status(self, wildcard_path):
    for path in glob.glob(os.path.join(wildcard_path, nodetool_status_path)):
      if not (ntStatus := NTStatusObject(path)).is_empty():
        return ntStatus
    print(Fore.RED + "\nNo parseable nodetool status output in {0}".format(os.path.join(wildcard_path, nodetool_status_path)) + Style.RESET_ALL)
    exit(1)
  
  def __print_header(self):
    print(Fore.WHITE + "-=" * 40)
    print("|" + Fore.CYAN + Style.BRIGHT + " {:^76} ".format(utils.get_path_segment_from_end(self.diag_path, 1)) \
      + Style.RESET_ALL + Fore.WHITE + "|")
    print("-=" * 40)
  
  def __print_sub_header(self, message):
    print(Fore.WHITE + "\n" + "--" * 40)
    print("|" + Fore.WHITE + Style.BRIGHT + " {:^76} ".format(message) + Style.RESET_ALL + Fore.WHITE + "|")
    print("--" * 40)

  def __print_diff(self, diffObject):
    if len(absent := diffObject.get_absent_list()) > 0:
      print(Fore.RED + "\nAbsent :: {0}".format(",".join(absent)) + Style.RESET_ALL)
    diff_found = False
    for key, diff, missing in diffObject.get_diff():
      if len(diff) > 0:
        diff_found = True
        print(Fore.MAGENTA + "\n{0}".format(key) + Style.RESET_ALL + Fore.WHITE + ":")
        for key in diff.keys():
          print(Fore.WHITE + "   {0}".format(key) + Fore.RED + Style.BRIGHT + " :: " + Style.RESET_ALL \
            + Fore.WHITE + "{0}".format(diff[key]) + Style.RESET_ALL)
      if len(missing) > 0:
        diff_found = True
        if len(diff) == 0:
          print(Fore.MAGENTA + "\n{0} ".format(key) + Style.RESET_ALL + Fore.WHITE + "(" \
            + Fore.MAGENTA + "{0}".format(next(iter(diffObject.get_merged_value(key).values()))) + Style.RESET_ALL \
            + Fore.WHITE + "):")
        print("   " + Fore.YELLOW + Style.BRIGHT + "Missing " + Fore.RED + "::" + Style.RESET_ALL \
          + Fore.WHITE + " {1}".format(key, ','.join(missing)) + Style.RESET_ALL)
    if not diff_found and len(absent) == 0:
      print(Fore.GREEN + "\nNo differences found" + Style.RESET_ALL)
    return diff_found


@click.command()
@click.argument('directory')
@click.option('--include-all', '-a', is_flag=True, default=False, help='Includes all available include options')
@click.option('--include-cassandra', '-c', is_flag=True, default=False, help='Includes or excludes cassandra.yamls in the diff')
@click.option('--include-dse', '-d', is_flag=True, default=False, help='Includes or excludes dse.yamls from the diff')
@click.option('--include-version', '-v', is_flag=True, default=False, help='Includes or excludes nodetool version output')
@click.option('--group-by-dc', '-g', is_flag=True, default=False, help='When performing diff, only compare files for nodes in the same DC')
@click.option('--exclude-data-directories', '-x', is_flag=True, help='Exclude all data directory location properties from diff (Applies to all files)')
def diagDiff(directory, include_all, include_cassandra, include_dse, include_version, group_by_dc, exclude_data_directories):
  if not include_all and not include_cassandra and not include_dse and not include_version:
    ctx = click.get_current_context()
    print(Fore.RED + "\nNeed to specify at least one file to diff\n\n" + Style.RESET_ALL + "{0}".format(ctx.get_help()))
    exit(1)
  diag = Diag(directory, group_by_dc)
  diag.diff(
    all=include_all,
    cassandra=include_cassandra,
    dse=include_dse,
    version=include_version,
    exclude_data_dirs=exclude_data_directories
  )