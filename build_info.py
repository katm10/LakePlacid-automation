import os
import json
from enum import Enum
from bin.paths import *
from gcc_options import *
import copy
import subprocess

stage_to_type = {
  GCCStage.PREPROCESS: ".c",
  GCCStage.INSTRUMENT: ".c",
  GCCStage.COMPILE: ".s",
  GCCStage.ASSEMBLE: ".o",
  GCCStage.LINK: ""
}

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
  def __init__(self, application, file=JSON_PATH):
    with open(file, "r") as f:
      self.compilation_dict = json.load(f)

    for key in self.compilation_dict.keys():
      self.compilation_dict[key] = CompilationInfo.from_json(self.compilation_dict[key])

    self.application = application
    self.leaves = set()

    self.build_dag()

  def build_dag(self):
    self.dag = {}
    visited = set()

    app_node = BuildInfoNode(self.compilation_dict[self.application], [], None, os.path.join(SCOUT_DIR, self.compilation_dict[self.application].stages[-1].name))
    visited.add(self.application)

    parents = [app_node]
    while len(parents) > 0:
      parent = parents.pop()
      is_leaf = True
      for input in parent.info.inputs:
        if input in visited:
          continue

        visited.add(input)

        if input not in self.compilation_dict.keys():
          continue

        child = BuildInfoNode(self.compilation_dict[input], [], parent, os.path.join(SCOUT_DIR, self.compilation_dict[input].stages[-1].name))
        parent.inputs.append(child)
        parents.append(child)
        is_leaf = False

      if is_leaf:
        self.leaves.add(parent)

  def build(self):
    frontier = self.leaves
    while len(frontier) > 0:
      next_frontier = set()
      for node in frontier:
        node.build()
        if node.output is not None:
          next_frontier.add(node.output)
      frontier = next_frontier

  # def insert(self, stage, compilation_info):
  #   nodes = self.leaves
  #   while len(nodes) > 0:
  #     node = nodes.pop()
  #     if stage in node.info["stages"]:
  #       if len(node.info["stages"]) == 1:
  #         pass
  #       else:
  #         # Split node first
  #         self.split(node, stage)
  #       return

  #     nodes.extend(node.inputs)
  #   pass

  def move(self, abs_src, abs_dst):
    rel_src = os.path.normpath(os.path.relpath(abs_src, ROOT_DIR))
    rel_dst = os.path.normpath(os.path.relpath(abs_dst, ROOT_DIR))

    for key, value in self.compilation_dict.items():
      if key == rel_src:
        value["rel_dir"] = os.path.dirname(rel_dst)
        value["abs_dir"] = os.path.dirname(abs_dst)
        value.output = os.path.basename(rel_dst)
        self.compilation_dict[rel_dst] = value
        del self.compilation_dict[key]
        break

class BuildInfoNode:
  def __init__(self, info, inputs, output, new_dir, compiler=None):
    self.info = info
    self.inputs = inputs
    self.output = output
    self.new_dir = new_dir
    self.compiler = compiler

  def front(self):
    front_node = self
    while len(front_node.inputs) == 1:
      front_node = front_node.inputs[0]

    return front_node

  def get_output_path(self):
    path = os.path.join(self.new_dir, self.info.output)
    if not os.path.exists(os.path.dirname(path)):
      os.makedirs(os.path.dirname(path))
    return path

  def build(self):
    command = []

    if self.compiler is not None:
      command.append(self.compiler)
    else:
      command.append(self.info.compiler)

    for stage in self.info.stages:
      command.extend(self.info.get_args_as_list(stage))
    command.extend(self.info.get_args_as_list(GCCStage.UNSPECIFIED))

    inputs = []
    if len(self.inputs) == 0:
      # We need to get the inputs from the source directory
      for input in self.info.inputs:
        inputs.append(os.path.join(self.info.abs_dir, input))
    else:
      for input in self.inputs:
        inputs.append(input.get_output_path())

    if self.info.stages[-1] == GCCStage.PREPROCESS:
      assert(len(inputs) == 1)
      command.extend(["-E", inputs[0]])
      print(" ".join(command))
      with open(self.get_output_path(), "w") as f:
        subprocess.run(command, stdout=f)
      return

    elif self.info.stages[-1] == GCCStage.INSTRUMENT:
      assert(len(inputs) == 1)
      command.extend([inputs[0], "--"])
      print(" ".join(command))
      with open(self.get_output_path(), "w") as f:
        subprocess.run(command, stdout=f)
      return

    elif self.info.stages[-1] == GCCStage.COMPILE:
      assert(len(inputs) == 1)
      command.extend(["-S", inputs[0]], "-o", self.get_output_path())
      print(" ".join(command))
      subprocess.run(command)
      return

    elif self.info.stages[-1] == GCCStage.ASSEMBLE:
      assert(len(inputs) == 1)
      command.extend(["-c", inputs[0], "-fPIC", "-o", self.get_output_path()])
      print(" ".join(command))
      subprocess.run(command)
      return

    elif self.info.stages[-1] == GCCStage.LINK:
      assert(len(inputs) > 0)
      command.extend(["-o", self.get_output_path()])
      command.extend(inputs)
      command.extend([os.path.join(LP_DIR, "support", "trace_support.c"), "-lpthread", "-levent"])

      print(" ".join(command))
      subprocess.Popen(command)
      return


  @staticmethod
  def split_and_construct(info, output):
    # Make the current node (fix the directory + filetype)

    
    filetype = stage_to_type(info.stages[0]) if info.stages[0] != GCCStage.COMPILE else stage_to_type(info.stages[1])
    dir = os.path.join(SCOUT_DIR, info.stages[0].name)

    # Figure out if we need to recurse

    if len(info.stages) == 1:
      return BuildInfoNode(info, [], output, os.path.join(SCOUT_DIR, info.stages[0].name))
    elif len(info.stages) == 2 and info.stages[-1] == GCCStage.ASSEMBLE:
      return BuildInfoNode(info, [], output, os.path.join(SCOUT_DIR, info.stages[0].name))
    else:
      back_info = copy.copy(info)

      back_info.stages = []
      if info.stages[-1] == GCCStage.ASSEMBLE:
        back_info.stages.extend(info.stages[-2:])
        info.stages.pop()
      else:
        back_info.stages.append(back_info.stages[-1])
      info.stages.pop()

      back = BuildInfoNode(back_info, [], output, os.path.join(SCOUT_DIR, back_info.stages[0].name))
      front = BuildInfoNode.split_and_construct(info, back)
      back.inputs.append(front)

      return back

class CompilationInfo:
  def __init__(self, compiler, argv=None):
    self.compiler = compiler
    self.abs_dir = os.path.normpath(os.getcwd())
    self.rel_dir = os.path.normpath(os.path.relpath(self.abs_dir, ROOT_DIR))
    self.args = CompilationInfo.empty_args()
    self.inputs = []
    if argv:
      self.last_stage = GCCStage.LINK
      self.parse(argv)
      self.path = os.path.normpath(os.path.join(self.rel_dir, self.output))
      self.first_stage = self.get_first_stage()

      if self.first_stage != self.last_stage:
        stages = [GCCStage.PREPROCESS, GCCStage.COMPILE, GCCStage.ASSEMBLE, GCCStage.LINK]
        while stages[0] != self.first_stage:
          stages.pop(0)
        while stages[-1] != self.last_stage:
          stages.pop()

        self.stages = stages
      else:
        self.stages = [self.first_stage]
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
        args[stage.name].append(GCCOption.from_json(option, stage))
    return args

  def to_json(self):
    return {
        "abs_dir": self.abs_dir,
        "rel_dir": self.rel_dir,
        "compiler": self.compiler,
        "inputs": self.inputs,
        "output": self.output,
        "args": self.args_to_json(),
        "stages": [stage.name for stage in self.stages]
    }

  @staticmethod
  def from_json(json_obj):
    info = CompilationInfo(json_obj["compiler"])
    info.abs_dir = json_obj["abs_dir"]
    info.rel_dir = json_obj["rel_dir"]
    info.inputs = json_obj["inputs"]
    info.output = json_obj["output"]
    info.args = info.args_to_obj(json_obj["args"])
    info.stages = []
    for stage in json_obj["stages"]:
      info.stages.append(GCCStage[stage])
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
          self.output = os.path.normpath(os.path.join(self.rel_dir, option.target))
          indx += 1
          continue
        self.args[option.stage.name].append(option)
      else:
        self.inputs.append(os.path.normpath(os.path.join(self.rel_dir, arg)))

      indx += 1

  def get_first_stage(self):
    file_type = self.inputs[0].split(".")[-1]
    for input in self.inputs:
      if input.split(".")[-1] != file_type:
        print("BAD INPUT: " + input + " " + file_type)
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

  def get_args_as_list(self, stage):
    args = []
    for arg in self.args[stage.name]:
      if arg.target is not None:
        if arg.target_type == InputType.FILE:
          arg.target = os.path.join(ROOT_DIR, self.rel_dir, arg.target)
          dir = os.path.dirname(arg.target)
          if not os.path.exists(dir):
            os.makedirs(dir, exist_ok=True) 
        elif arg.target_type == InputType.DIR:
          arg.target = os.path.join(ROOT_DIR, self.rel_dir, arg.target)
          if not os.path.exists(arg.target):
            os.makedirs(arg.target, exist_ok=True)

        if arg.separator == " ":
          args.extend([arg.option, arg.target])
        else:
          args.append(arg.option + arg.separator + arg.target)
      
      else:
        args.append(arg.option)

    return args
