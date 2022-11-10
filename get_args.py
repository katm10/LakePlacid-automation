import sys
import os
import json
from instrument import ROOT_DIR, LP_DIR 
from compilation_info import CompilationInfo

def main():
  info_file = os.path.join(LP_DIR, "compilation_info.json")

  if not os.path.exists(info_file):
    with open(info_file, "w") as f:
      json_obj = {
        "compilation": [],
        "linking": []
      }
      json.dump(json_obj, f)

  info = CompilationInfo(sys.argv[1:])
  info.update(info_file)

if __name__ == "__main__":
  main()

