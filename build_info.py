import os
import json
from enum import Enum
from bin.paths import *
from gcc_options import *

# {
#     "<path relative to ROOT_DIR>": {
#         "abs_dir": "<abs_dir>",
#         "rel_dir": "<rel_dir>",
#         "command": "<command>",
#         "inputs": [],
#         "output": "<output>",
#         "args": {
#             "preprocessor": [
#                 {
#                     "option": "<option>",
#                     "target": "<target>",
#                     "target_type": "<target_type>",
#                     "separator": "<separator>",
#                 }
#             ],
#             "compiler": [],
#             "assembler": [],
#             "linker": [],
#             "unspecified": [],
#         },
#         "stages": [],
#     }
# }


class BuildInfoDAG:
  def __init__(self, file=JSON_PATH):
    with open(file, "r") as f:
      self.dag = json.load(f)

  def move(self, abs_src, abs_dst):
    rel_src = os.path.relpath(abs_src, ROOT_DIR)
    rel_dst = os.path.relpath(abs_dst, ROOT_DIR)

    for key, value in self.dag.items():
      if key == rel_src:
        value["rel_dir"] = os.path.dirname(rel_dst)
        value["abs_dir"] = os.path.dirname(abs_dst)
        value.output = os.path.basename(rel_dst)
        self.dag[rel_dst] = value
        del self.dag[key]
        break


class CompilationInfo:
  def __init__(self, compiler, argv=None):
    self.compiler = compiler
    self.abs_dir = os.getcwd()
    self.rel_dir = os.path.relpath(self.abs_dir, ROOT_DIR)
    self.args = CompilationInfo.empty_args()
    self.inputs = []
    if argv:
      self.last_stage = GCCStage.LINK
      self.parse(argv)
      self.path = os.path.join(self.rel_dir, self.output)
      self.first_stage = self.get_first_stage()

      if self.first_stage != self.last_stage:
        stages = ["PREPROCESS", "COMPILE", "ASSEMBLE", "LINK"]
        while stages[0] != self.first_stage.name:
          stages.pop(0)
        while stages[-1] != self.last_stage.name:
          stages.pop()

        self.stages = stages
      else:
        self.stages = [self.first_stage.name]
    else:
      self.path = None
      self.last_stage = None
      self.first_stage = None
      self.stages = None

  @staticmethod
  def empty_args():
    args = {}
    for stage in GCCStage:
      args[stage.name] = []
    return args

  def args_to_json(self):
    args = {}
    for stage in GCCStage:
      args[stage.name] = []
      for option in self.args[stage.name]:
        args[stage.name].append(option.to_json())
    return args

  def args_to_obj(self, args_json):
    args = CompilationInfo.empty_args()
    for stage in GCCStage:
      for option in args_json[stage.name]:
        args[stage.name].append(GCCOption.from_json(option))
    return args

  def to_json(self):
    return {
        "abs_dir": self.abs_dir,
        "rel_dir": self.rel_dir,
        "compiler": self.compiler,
        "inputs": self.inputs,
        "output": self.output,
        "args": self.args_to_json(),
        "stages": self.stages
    }

  @staticmethod
  def from_json(json_obj):
    info = CompilationInfo(json_obj["compiler"])
    info.abs_dir = json_obj["abs_dir"]
    info.rel_dir = json_obj["rel_dir"]
    info.inputs = json_obj["inputs"]
    info.output = json_obj["output"]
    info.args = info.args_to_obj(json_obj["args"])
    info.stages = json_obj["stages"]
    return info

  def parse(self, argv):
    indx = 0
    while indx < len(argv):
      arg = argv[indx].strip()
      if arg[0] == "-":
        option, indx = GCCOption.construct(arg, indx, argv)

        if option.option == "-E":
          self.last_stage = GCCStage.PREPROCESS
        elif option.option == "-S":
          self.last_stage = GCCStage.COMPILE
        elif option.option == "-c":
          self.last_stage = GCCStage.ASSEMBLE
          self.compile_only = True
          indx += 1
          continue
        elif option.option == "-o":
          self.output = os.path.join(self.rel_dir, option.target)
          indx += 1
          continue
        self.args[option.stage.name].append(option)
      else:
        self.inputs.append(os.path.join(self.rel_dir, arg))

      indx += 1

  def get_first_stage(self):
    file_type = self.inputs[0].split(".")[-1]
    for input in self.inputs:
      if input.split(".")[-1] != file_type:
        return GCCStage.UNSPECIFIED

    if file_type in ("c", "h", "S"):
      return GCCStage.PREPROCESS
    elif file_type == "i":
      return GCCStage.COMPILE
    elif file_type == "s":
      return GCCStage.ASSEMBLE
    elif file_type in ("o", "so"):
      return GCCStage.LINK

  def update(self, file=JSON_PATH):
    with open(file, "r") as f:
      json_obj = json.load(f)

    value = self.to_json()
    json_obj[self.path] = value

    with open(file, "w") as f:
      json.dump(json_obj, f)
