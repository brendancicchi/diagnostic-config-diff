class NTVersionObject:
  def __init__(self, nodetool_version_file):
    self.nodetool_version_file = nodetool_version_file
    self.version = self.__parse()

  def get(self):
    return self.version

  def __parse(self):
    with open(self.nodetool_version_file, 'r') as fh:
      for line in fh:
        line_tokens = line.split()      
        if line.startswith("ReleaseVersion:", 0, 15):
          return line_tokens[1]
    return None