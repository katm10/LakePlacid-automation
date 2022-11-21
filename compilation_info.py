import json
import os 
import gcc_options
from bin.paths import *

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
    self.command = json_obj["command"]
    self.output = json_obj["output"]
    self.inputs = json_obj["inputs"]
    self.preprocessor_args = gcc_options.GCCOption.json_to_args(json_obj["args"]["preprocessor"], gcc_options.GCCStage.PREPROCESS)
    self.compiler_args = gcc_options.GCCOption.json_to_args(json_obj["args"]["compiler"], gcc_options.GCCStage.COMPILE)
    self.assembler_args = gcc_options.GCCOption.json_to_args(json_obj["args"]["assembler"], gcc_options.GCCStage.ASSEMBLE)
    self.linker_args = gcc_options.GCCOption.json_to_args(json_obj["args"]["linker"], gcc_options.GCCStage.LINK)
    self.unspecified_args = gcc_options.GCCOption.json_to_args(json_obj["args"]["unspecified"], gcc_options.GCCStage.UNSPECIFIED)

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

  def convert_args(self, init_args, directory):

    if not os.path.samefile(self.directory, ROOT_DIR):
        rel_dir = os.path.relpath(self.directory, ROOT_DIR)
        directory = os.path.join(directory, rel_dir)
        
    args = []
    for arg in init_args:
      if arg.target is not None:
        if arg.target_type == gcc_options.InputType.FILE:
          arg.target = os.path.join(directory, arg.target)
          dir = os.path.dirname(arg.target)
          os.makedirs(dir, exist_ok=True) 
        elif arg.target_type == gcc_options.InputType.DIR:
          arg.target = os.path.join(directory, arg.target)
          os.makedirs(arg.target, exist_ok=True)

        if arg.separator == " ":
          args.extend([arg.option, arg.target])
        else:
          args.append(arg.option + arg.separator + arg.target)
    return args

  def get_preprocessor_args(self, directory = ROOT_DIR):
    return self.convert_args(self.preprocessor_args, directory)

  def get_compiler_args(self, directory = ROOT_DIR):
    return self.convert_args(self.compiler_args, directory)

  def get_assembler_args(self, directory = ROOT_DIR):
    return self.convert_args(self.assembler_args, directory)
  
  def get_linker_args(self, directory = ROOT_DIR):
    return self.convert_args(self.linker_args, directory)

  def get_unspecified_args(self, directory = ROOT_DIR):
    return self.convert_args(self.unspecified_args, directory)

  def get_output(self, directory = None):
    return self.output

  def get_inputs(self, directory = None):
    return " ".join(self.inputs)

  def parse(self):
    rel_dir = os.path.relpath(self.directory, ROOT_DIR)
    self.output = os.path.join(rel_dir, "a.o")
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
          self.output = os.path.join(rel_dir, option.target)
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
        elif option.stage == gcc_options.GCCStage.UNSPECIFIED:
          self.unspecified_args.append(option.to_dict())

      else:
        self.inputs.append(os.path.join(rel_dir, arg))

      indx += 1
    

      
