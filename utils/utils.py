import ipaddress

def is_ip (str):
  try:
    ipaddress.ip_address(str)
  except ValueError:
    return False
  return True

# Determine the ip address based on the absolute path to the cassandra.yaml
#   e.g. /my/path/to/diag/nodes/127.0.0.1/conf/cassandra/cassandra.yaml
def get_path_segment_from_end(path, segment_num):
  path_tokens = path.split('/')
  return path_tokens[len(path_tokens) - segment_num]