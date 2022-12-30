import sys
from build_info import *
from bin.paths import *

# Need to 
# 1. Read in the build_info.json file <- just call this from BuildInfoDAG
# 2. Parse out the src, dest
# 3. Edit and write out the new build_info.json file

def parse_mv(argv):
    if len(argv) < 3:
        print("Invalid number of arguments")
        sys.exit(1)

    src_dst = []

    for arg in argv[1:]:
        if arg[0] != "-":
            src_dst.append(arg)

    assert(len(src_dst) == 2)
    return src_dst

if __name__ == "__main__":
  src, dst = parse_mv(sys.argv)
  buildinfo = BuildInfoDAG()
  buildinfo.move(src, dst)