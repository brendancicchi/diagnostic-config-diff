import ipaddress
from diff.utils import utils

class NTRingObject:
  def __init__(self, nodetool_ring_file):
    self.nodetool_ring_file = nodetool_ring_file
    self.ip_token_map = self.__parse()
    
  def __parse(self):
    with open(self.nodetool_ring_file, 'r') as fh:
      dc = ""
      ip_token_map = dict()
      for line in fh:
        line_tokens = line.split()      
        if line.startswith("Datacenter:", 0, 11):
          dc = line_tokens[1]
        if len(line_tokens) > 0 and utils.is_ip(line_tokens[0]):
          if not line_tokens[0] in ip_token_map.keys():
            ip_token_map[line_tokens[0]] = {
              'dc': dc,
              'rack': line_tokens[1],
              'ownership': line_tokens[6],
              'tokens': {line_tokens[7]}
            }
          else:
            ip_token_map[line_tokens[0]]['tokens'].add(line_tokens[7])
    return ip_token_map