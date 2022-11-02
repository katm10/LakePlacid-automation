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
    self.assembler_args = []
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
        "assembler": self.assembler_args,
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
    self.assembler_args = json_obj["args"]["assembler"]
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
    indx = 0
    while indx < len(self.args):
      arg = self.args[indx].strip()
      if arg[0] == '-':
        option, indx = gcc_options.GCCOption.construct(arg, indx, self.args)

        if option.option == "-c":
          self.compile_only = True
          indx += 1
          continue
        elif option.option == "-o":
          self.output = option.target
          indx += 1
          continue

        if option.stage == gcc_options.GCCStage.PREPROCESS:
          self.preprocessor_args.append(option.to_dict())
        elif option.stage == gcc_options.GCCStage.COMPILE:
          self.compiler_args.append(option.to_dict())
        elif option.stage == gcc_options.GCCStage.ASSEMBLE:
          self.assembler_args.append(option.to_dict())
        elif option.stage == gcc_options.GCCStage.LINK:
          self.linker_args.append(option.to_dict())
        else:
          self.unspecified_args.append(option.to_dict())

      else:
        self.inputs.append(arg)

      indx += 1
    

      