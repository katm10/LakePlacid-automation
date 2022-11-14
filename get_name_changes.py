import sys
import os
import json
from bin.paths import *

MV_JSON = "mv_info.json"

def generate_mv_json(make_txt, json_path):
  directory = os.getcwd()
  name_map = {}
  with open(make_txt, 'r') as f:
    lines = f.readlines()
    for line in lines:
      if line.startswith("mv "):
        args = [arg.strip() for arg in line.split(" ")[1:] if (not arg.startswith("-") and arg != "")]
        if len(args) != 2:
          print("Error: mv command has incorrect number of arguments")
          sys.exit(1)
        else:
          init_path = args[0]
          final_path = args[1]
          name_map[init_path] = final_path

  dict_obj = {"directory": directory, "file_changes": name_map}
  
  with open(json_path, 'w') as f:
      json.dump(dict_obj, f)

def main():
  if not os.path.exists(MV_JSON):
    with open(MV_JSON, "w") as f:
      json_obj = {
        "directory": "",
        "file_changes": {}
      }
      json.dump(json_obj, f)
  
  
  
if __name__ == "__main__":  
  make_txt = sys.argv[1]
  generate_mv_json(make_txt, MV_JSON)
