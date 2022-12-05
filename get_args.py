import sys
import os
import json
from bin.paths import * 
from build_info import CompilationInfo

def main():
  if not os.path.exists(JSON_FILE):
    with open(JSON_FILE, "w") as f:
      json.dump({}, f)

  info = CompilationInfo(sys.argv[1], sys.argv[2:])
  info.update()

if __name__ == "__main__":
  main()

