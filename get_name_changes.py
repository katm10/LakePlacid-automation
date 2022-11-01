import sys
import os
import json

def main():
  make_txt = sys.argv[1]

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
  
  with open("name_changes.json", 'w') as f:
      json.dump(name_map, f)
  
if __name__ == "__main__":
    main()

