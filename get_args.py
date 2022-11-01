import sys
import os
import json
from compilation_info import CompilationInfo

def main():
  dir = "instrumentation"
  info_file = "compilation_info.json"
  info_path = os.path.join(dir, info_file)

  if not os.path.exists(dir):
    os.makedir(dir)

  if not os.path.exists(info_path):
    with open(info_path, "w") as f:
      json_obj = {
        "compilation": [],
        "linking": []
      }
      json.dump(json_obj, f)

  info = CompilationInfo(sys.argv[1:])
  info.update(info_path)

if __name__ == "__main__":
  main()

