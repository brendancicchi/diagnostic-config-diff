
class NTStatusObject:
  def __init__(self, nodetool_status_file):
    self.nodetool_status_file = nodetool_status_file
    self.dc_to_ip_map, self.ip_info_map = self.__parse()

  def is_empty(self):
    if len(self.dc_to_ip_map) == 0:
      return True
    else:
      return False

  def __parse(self):
    dc_to_ip_map = {}
    ip_info_map = {}
    with open(self.nodetool_status_file, 'r') as fh:
      dc = ""
      for line in fh:
        line_tokens = line.split()      
        if line.startswith("Datacenter:", 0, 11):
          dc = line_tokens[1]
        if len(line_tokens) > 0 and line_tokens[0] in ['UN', 'DN', 'UJ', 'UM', 'DL', 'DS']:
          if dc in dc_to_ip_map.keys():
            dc_to_ip_map[dc].add(line_tokens[1])
          else:
            dc_to_ip_map[dc] = {line_tokens[1]}
          ip_info_map[line_tokens[1]] = {
            'status': line_tokens[0],
            'load': line_tokens[2] + ' ' + line_tokens[3],
            'tokens': line_tokens[4],
            'ownership': line_tokens[5],
            'host_id': line_tokens[6],
            'rack': line_tokens[7],
            'dc': dc
          }
    return dc_to_ip_map, ip_info_map