from sortedcontainers import SortedSet

# blacklist JVM properties because should be unique to each node
blacklist = [
  '-Dmx4jaddress',
  '-Djava.rmi.server.hostname',
  '-javaagent:/home/automaton/jolokia-jvm-agent.jar'
]

class JVMOptsObject:
  def __init__(self, ip, java_opts_file):
    self.ip = ip
    self.java_opts_file = java_opts_file
    self.options = SortedSet([])

  def parse(self):
    with open(self.java_opts_file, 'r') as fh:
      for opt in fh.readline().split(maxsplit=8)[8].split():
        opt_tokens = opt.split('=', maxsplit=1)
        if not opt_tokens[0] in blacklist:
          if len(opt_tokens) > 1:
            self.opts_set.add("=".join(opt_tokens))
          else:
            self.opts_set.add(opt_tokens[0])