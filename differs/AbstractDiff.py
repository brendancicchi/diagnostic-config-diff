from abc import ABC, abstractmethod
from colorama import Fore
from colorama import Style
from utils import utils

class AbstractDiff(ABC):
  def __init__(self, file_paths):
    self._file_paths = file_paths
    self._included_ips = [] # Appended to during __get_parsed_objects
    self._absent_list = [] # Appended to during __get_parsed_objects
    self._merged = dict() # Required format: {property: {ipset: value, ipset2: value2, ...}}
    self._diff_results = []

  def get_absent_list(self):
    return self._absent_list
  
  def get_diff(self):
    return self._diff_results

  def get_merged_value(self, key):
    return self._merged.get(key)

  def print_merged(self):
    for key in self._merged.keys():
      print(Fore.MAGENTA + "\n{0}".format(key) + Fore.RESET + Fore.WHITE + ":")
      for nested_key in self._merged[key].keys():
        print("   {0}".format(nested_key) + Fore.RED + Style.BRIGHT + " :: " + Style.RESET_ALL \
          + Fore.WHITE + "{0}".format(self._merged[key][nested_key]))

  @abstractmethod
  def _diff_merged(self):
    pass

  @abstractmethod
  def _merge_objects(self):
    pass

  def _get_parsed_objects(self, ParseObject, tail_path_index):
    parsed_objects = []
    for path in self._file_paths:
      ip = utils.get_path_segment_from_end(path, tail_path_index)
      if (parsed_object := ParseObject(path).get()) != None:
        self._included_ips.append(ip)
        parsed_objects.append((ip, parsed_object))
      else:
        self._absent_list.append(ip)
    return parsed_objects

  def _can_combine_keys_for_identical_value(self, new_value, new_key, my_dict):
    for key, value in my_dict.items():
      if value == new_value:
        new_key = key + "," + new_key
        my_dict[new_key] = value
        my_dict.pop(key)
        return True
    return False

  def _check_for_all_ips(self, ip_value_dict):
    all_ips_in_dict = set()
    for key in ip_value_dict.keys():
      all_ips_in_dict = all_ips_in_dict.union(set(key.split(',')))
    return all_ips_in_dict.symmetric_difference(self._included_ips)

  # Returns tuple (key, dict-with-different-property-values, set-with-missing-ips)
  # Either the dict or the set could be empty (but not both)
  def _diff_merged(self):
    diff_results = []
    missing_results = []
    for key in self._merged.keys():
      missing = self._check_for_all_ips(self._merged[key])
      if len(self._merged[key]) > 1:
        diff_results.append((key, self._merged[key], missing))
      elif len(missing) > 0: 
        diff_results.append((key, (), missing))
    return diff_results
