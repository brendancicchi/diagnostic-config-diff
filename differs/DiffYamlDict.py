import os
from diff.differs.AbstractDiff import AbstractDiff
from diff.parsers.ParseYaml import YamlObject
from diff.utils import utils

class DiffYamlDict(AbstractDiff):
  def __init__(self, yaml_file_paths, always_unique_keys=[]):
    super().__init__(yaml_file_paths)
    self.__always_unique_keys = always_unique_keys
    self._merged = self._merge_objects()
    self._diff_results = self._diff_merged()
  
  def _merge_objects(self):
    final_dict = {}
    for ip, yaml_object in self._get_parsed_objects(YamlObject, 4):
      for key, value in yaml_object.items():
        self.__merge_objects_recursive(value, ip, key, final_dict, 0)
    return final_dict

  def __merge_objects_recursive(self, sub_yaml_object, ip, traversal_path, final_dict, counter):
    if isinstance(sub_yaml_object, dict):
      for key, value in sub_yaml_object.items():
        self.__merge_objects_recursive(value, ip, traversal_path + '.' + key, final_dict, counter)
    elif isinstance(sub_yaml_object, list):
      temp_counter = counter
      for item in sub_yaml_object:
        if counter > 0:
          if counter > 1:
            traversal_path = os.path.splitext(traversal_path)[0] + ".{0}".format(counter)
          else:
            traversal_path += ".{0}".format(counter)
        counter += 1
        if isinstance(item, dict) or isinstance(item, list):
          self.__merge_objects_recursive(item, ip, traversal_path, final_dict, 0)
        else:
          self.__add_property(traversal_path, ip, item, final_dict)
      counter = temp_counter
    else:
      self.__add_property(traversal_path, ip, sub_yaml_object, final_dict)

  def __add_property(self, key, ip, value, final_dict):
    if key not in self.__always_unique_keys:
      if key in final_dict.keys():
        if not self._can_combine_keys_for_identical_value(value, ip, final_dict[key]):
            final_dict[key].update({ip: value})
      else:
        final_dict[key] = {ip: value}
    return final_dict