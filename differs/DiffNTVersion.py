from diff.parsers.ParseNTVersion import NTVersionObject
from diff.utils import utils
from diff.differs.AbstractDiff import AbstractDiff


class DiffNTVersion(AbstractDiff):
  def __init__(self, version_file_paths):
    super().__init__(version_file_paths)
    self._merged = self._merge_objects()
    self.__version = self.__assign_version() # None if there is not a single value for all nodes (excludes absent)
    self._diff_results = self._diff_merged()

  def get_version(self):
    return self.__version

  def _merge_objects(self):
    final_dict = {'ReleaseVersion': {}}
    for ip, version in self._get_parsed_objects(NTVersionObject, 3):
      if not self._can_combine_keys_for_identical_value(version, ip, final_dict['ReleaseVersion']):
        final_dict['ReleaseVersion'].update({ip: version})
    return final_dict
  
  def __assign_version(self):
    if len(self._merged) > 0:
      if len(version_dict := next(iter(self._merged.values()))) == 1:
        return next(iter(version_dict.values()))
    return None
