import sys
import os
import json
from bin.paths import * 
from build_info import CompilationInfo

def main():
  if not os.path.exists(JSON_PATH):
    with open(JSON_PATH, "w") as f:
      json.dump({}, f)

  info = CompilationInfo(sys.argv[1], sys.argv[2:])
  info.update()

if __name__ == "__main__":
  main()

