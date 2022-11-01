import json
import os 
import gcc_options

# [
#   {
#     "directory": "/home/kmohr/Documents/MIT/SuperUROP/workspace/makefile-for-c",
#     "compile-only": bool,
#     "output": "src/foo-test.o",
#     "inputs": [
      
#     ],
#     "args": {
#       "preprocessor": [],
#       "compiler": [],
#       "linker": [],
#       "unspecified": []
#     }
#   }
# ]

class CompilationInfo:
  def __init__(self, command = None):
    self.compile_only = False
    self.output = None
    self.inputs = []
    self.preprocessor_args = []
    self.compiler_args = []
    self.linker_args = []
    self.unspecified_args = []
    self.command = command

    if command is None:
      self.args = None
      self.directory = None
    else:
      self.args = command
      self.directory = os.getcwd()
      self.parse()

  def to_dict(self):
    dict_obj = {
      "directory": self.directory,
      "command": self.command,
      "output": self.output,
      "inputs": self.inputs,
      "args": {
        "preprocessor": self.preprocessor_args,
        "compiler": self.compiler_args,
        "linker": self.linker_args,
        "unspecified": self.unspecified_args
      }
    }

    return dict_obj

  def from_json(self, json_obj):
    self.directory = json_obj["directory"]
    self.compile_only = json_obj["compile-only"]
    self.output = json_obj["output"]
    self.inputs = json_obj["inputs"]
    self.preprocessor_args = json_obj["args"]["preprocessor"]
    self.compiler_args = json_obj["args"]["compiler"]
    self.linker_args = json_obj["args"]["linker"]
    self.unspecified_args = json_obj["args"]["unspecified"]

  def update(self, json_file):
    with open(json_file, "r") as f:
      json_obj = json.load(f)

    entry = self.to_dict()
    if self.compile_only:
      json_obj["compilation"].append(entry)
    else:
      json_obj["linking"].append(entry)
    
    with open(json_file, "w") as f:
      json.dump(json_obj, f)

  def get_preprocessor_arg_str(self):
    return " ".join(self.preprocessor_args)

  def get_compiler_arg_str(self):
    return " ".join(self.compiler_args)
  
  def get_linker_arg_str(self):
    return " ".join(self.linker_args)

  def get_unspecified_arg_str(self):
    return " ".join(self.unspecified_args)

  def get_output(self):
    return self.output

  def get_inputs(self):
    return " ".join(self.inputs)

  def parse(self):
    args = iter(self.args)
    
    while True:
      option = arg_iter.next().strip()

      double_dash = False
      is_flag = False

      if option.startswith("--"):
        option = option[2:]
        double_dash = True
        is_flag = True
      elif option.startswith("-"):
        option = option[1:]
        is_flag = True
      
      if is_flag:
        option_info = GCCOption.find_matching_arg(option, double_dash)
        return GCCOption.construct(option, option_info, arg_iter)
      else:
        return GCCTarget(option)