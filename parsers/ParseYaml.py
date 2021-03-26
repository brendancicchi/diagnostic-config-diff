import os
import yaml

class YamlObject:
  def __init__(self, yaml_file):
    if os.path.exists(yaml_file):
      with open(yaml_file, 'r') as fh:
        self.yaml_object = yaml.full_load(fh)
    else:
      self.yaml_object = None
  
  def get(self):
    return self.yaml_object