import os
import json
from bin.paths import *
from gcc_options import *
import copy
import subprocess
from dataclasses import dataclass
from typing import List, Dict, Set

"""
{
    "<path relative to ROOT_DIR>": {
        "rel_dir": "<rel_dir>",
        "command": "<command>",
        "inputs": [],
        "output": "<output>",
        "args": {
            "preprocessor": [
                {
                    "option": "<option>",
                    "target": "<target>",
                    "target_type": "<target_type>",
                    "separator": "<separator>",
                }
            ],
            "compiler": [],
            "assembler": [],
            "linker": [],
            "unspecified": [],
        },
        "stages": [],
    }
}
"""

stage_to_type = {
    GCCStage.PREPROCESS: ".c",
    GCCStage.INSTRUMENT: ".c",
    GCCStage.COMPILE: ".s",
    GCCStage.ASSEMBLE: ".o",
    GCCStage.LINK: "",
}


def get_stage_from_inputs(inputs):
    ext_to_stage = {
        "c": GCCStage.PREPROCESS,
        "h": GCCStage.PREPROCESS,
        "S": GCCStage.PREPROCESS,
        "i": GCCStage.COMPILE,
        "s": GCCStage.ASSEMBLE,
        "o": GCCStage.LINK,
        "so": GCCStage.LINK,
        "a": GCCStage.LINK,
    }

    stage = ext_to_stage[inputs[0].split(".")[-1]]
    for input in inputs:
        if ext_to_stage[input.split(".")[-1]] != stage:
            print(f"WARNING: inputs are of different types: {', '.join(inputs)}")
            return GCCStage.UNSPECIFIED

    return stage


@dataclass
class CompilationInfo:
    args: Dict[GCCStage, List[GCCOption]]
    inputs: List[str]
    output: str
    compiler: str
    rel_dir: str
    stages: List[GCCStage]

    @staticmethod
    def empty_args():
        args = {}
        for stage in GCCStage:
            args[stage.name] = []
        return args

    @staticmethod
    def from_json(json_obj):
        return CompilationInfo(
            args=CompilationInfo.args_to_obj(json_obj["args"]),
            inputs=json_obj["inputs"],
            output=json_obj["output"],
            compiler=json_obj["compiler"],
            rel_dir=json_obj["rel_dir"],
            stages=[GCCStage[stage] for stage in json_obj["stages"]],
        )

    @staticmethod
    def construct(command: str) -> "CompilationInfo":
        path, compiler, *argv = command.split(" ")
        rel_dir = os.path.normpath(os.path.relpath(path, ROOT_DIR))

        compilation_info = CompilationInfo(
            args=CompilationInfo.empty_args(),
            inputs=[],
            output=None,
            compiler=compiler,
            rel_dir=rel_dir,
            stages=[],
            first_stage=None,
            last_stage=GCCStage.LINK,
        )

        compilation_info.parse(argv)
        return compilation_info

    @staticmethod
    def args_to_obj(args_json):
        args = CompilationInfo.empty_args()
        for stage in GCCStage:
            for option in args_json[stage.name]:
                args[stage.name].append(GCCOption.from_json(option, stage))
        return args

    def parse(self, argv):
        indx = 0
        last_stage = GCCStage.LINK
        while indx < len(argv):
            arg = argv[indx].strip()
            if arg[0] == "-":
                option, indx = GCCOption.construct(arg, indx, argv)

                if option.option == "-E":
                    last_stage = GCCStage.PREPROCESS
                elif option.option == "-S":
                    last_stage = GCCStage.COMPILE
                elif option.option == "-c":
                    last_stage = GCCStage.ASSEMBLE
                    indx += 1
                    continue
                elif option.option == "-o":
                    self.output = os.path.normpath(
                        os.path.join(self.rel_dir, option.target)
                    )
                    indx += 1
                    continue
                self.args[option.stage.name].append(option)
            else:
                self.inputs.append(os.path.normpath(os.path.join(self.rel_dir, arg)))
            indx += 1

        first_stage = get_stage_from_inputs(self.inputs)
        if first_stage == last_stage:
            self.stages = [first_stage]
            return

        stages = [
            GCCStage.PREPROCESS,
            GCCStage.COMPILE,
            GCCStage.ASSEMBLE,
            GCCStage.LINK,
        ]
        while stages[0] != first_stage:
            stages.pop(0)
        while stages[-1] != last_stage:
            stages.pop()

        self.stages = stages

    def args_to_json(self):
        args = {}
        for stage in GCCStage:
            args[stage.name] = []
            for option in self.args[stage.name]:
                args[stage.name].append(option.to_json())
        return args

    def to_json(self):
        return {
            "rel_dir": self.rel_dir,
            "compiler": self.compiler,
            "inputs": self.inputs,
            "output": self.output,
            "args": self.args_to_json(),
            "stages": [stage.name for stage in self.stages],
        }

    def update(self, file=JSON_PATH):
        with open(file, "r") as f:
            json_obj = json.load(f)

        if self.output in json_obj.keys():
            raise Exception(self.output + " already exists")

        value = self.to_json()
        json_obj[self.output] = value

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


@dataclass
class BuildInfoNode:
    info: CompilationInfo
    inputs: List["BuildInfoNode"]
    outputs: List["BuildInfoNode"]
    new_dir: str
    compiler: str
    built: bool = False

    def ready(self):
        for input in self.inputs:
            if not input.built:
                return False

        return True

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

    def build_command(self):
        command = []

        if self.compiler is not None:
            command.append(self.compiler)
        else:
            command.append(self.info.compiler)

        input_paths = set(self.info.inputs)
        inputs = []
        for input in self.inputs:
            path = input.info.output
            input_paths.discard(path)
            inputs.append(input.get_output_path())

        for path in input_paths:
            inputs.append(os.path.join(ROOT_DIR, path))

        if self.info.stages[-1] == GCCStage.PREPROCESS:
            assert len(inputs) == 1
            command.extend(["-E", inputs[0]])

        elif self.info.stages[-1] == GCCStage.INSTRUMENT:
            assert len(inputs) == 1
            original_info = self.inputs[0].info
            assert len(original_info.inputs) == 1
            original_path = os.path.join(ROOT_DIR, original_info.inputs[0])
            command.extend([original_path, inputs[0], "--"])

        elif self.info.stages[-1] == GCCStage.COMPILE:
            assert len(inputs) == 1
            command.extend(["-S", inputs[0]], "-o", self.get_output_path())

        elif self.info.stages[-1] == GCCStage.ASSEMBLE:
            print(self.get_output_path() + " has inputs " + " ".join(inputs))
            assert len(inputs) == 1
            command.extend(
                [
                    "-c",
                    inputs[0],
                    "-Wno-constant-logical-operand",
                    "-fPIC",
                    "-o",
                    self.get_output_path(),
                ]
            )

        elif self.info.stages[-1] == GCCStage.LINK:
            assert len(inputs) > 0
            command.extend(["-o", self.get_output_path()])
            command.extend(inputs)
            command.extend(
                [
                    os.path.join(LP_DIR, "support", "trace_support.c"),
                    "-lpthread",
                    "-levent",
                ]
            )

        if self.info.stages[-1] != GCCStage.INSTRUMENT:
            # Don't include flags when instrumenting
            for stage in self.info.stages:
                command.extend(self.info.get_args_as_list(stage))
            command.extend(self.info.get_args_as_list(GCCStage.UNSPECIFIED))

        return command

    def run_command(self, command):
        if self.info.stages[-1] == GCCStage.PREPROCESS:
            with open(self.get_output_path(), "w") as f:
                subprocess.run(command, stdout=f)

        elif self.info.stages[-1] == GCCStage.INSTRUMENT:
            with open(self.get_output_path(), "w") as f:
                subprocess.run(command, stdout=f)

        elif self.info.stages[-1] == GCCStage.COMPILE:
            subprocess.run(command)

        elif self.info.stages[-1] == GCCStage.ASSEMBLE:
            subprocess.run(command)

        elif self.info.stages[-1] == GCCStage.LINK:
            subprocess.run(command)

    def build(self, print_only=False):
        assert not self.built

        if not self.ready():
            print(self.get_output_path() + " is NOT ready")
            assert False

        self.built = True
        command = self.build_command()
        print(" ".join(command))
        if not print_only:
            self.run_command(command)

    def split(self, stage):
        stage_indx = self.info.stages.index(stage)

        # Include the stage we want to split on in the back node
        back_info_stages = self.info.stages[stage_indx:]
        front_info_stages = self.info.stages[:stage_indx]

        # Fix the output filetype for the front node
        output_file, _ = os.path.splitext(self.info.output)
        front_info_output = output_file + stage_to_type[self.info.stages[-1]]

        # Fix the input filetype for the back node
        back_info_inputs = [self.info.output]

        back_info = CompilationInfo(
            args=self.info.args,
            compiler=self.info.compiler,
            inputs=back_info_inputs,
            output=self.info.output,
            stages=back_info_stages,
            rel_dir=self.info.rel_dir,
        )

        front_info = CompilationInfo(
            args=self.info.args,
            compiler=self.info.compiler,
            inputs=self.info.inputs,
            output=front_info_output,
            stages=front_info_stages,
            rel_dir=self.info.rel_dir,
        )

        back = BuildInfoNode(
            back_info, [], self.outputs, os.path.join(self.new_dir), self.compiler
        )

        self.info = front_info

        for output in self.outputs:
            output.inputs.remove(self)
            output.inputs.append(back)

        self.outputs = [back]
        self.new_dir = os.path.join(
            os.path.split(self.new_dir)[0], self.info.stages[-1].name
        )

        back.inputs = [self]

        return back


@dataclass
class BuildInfoDAG:
    compilation_dict: Dict[str, CompilationInfo]
    applications: List[str]
    leaves: Dict[str, BuildInfoNode]
    compiler: str
    insertions: List[Tuple[GCCStage, str, str]]
    output_dir: str

    @staticmethod
    def construct_from_json(output_dir, applications=[], file=JSON_PATH):
        with open(file, "r") as f:
            compilation_dict = json.load(f)

        for key in compilation_dict.keys():
            compilation_dict[key] = CompilationInfo.from_json(compilation_dict[key])

        if len(applications) == 0:
            # Find all executables in the compilation dict
            applications = [
                key
                for key in compilation_dict.keys()
                if os.path.splitext(compilation_dict[key].output)[1] == ""
            ]

        for stage in GCCStage:
            if not os.path.exists(os.path.join(output_dir, stage.name)):
                os.makedirs(os.path.join(output_dir, stage.name))

        return BuildInfoDAG(
            compilation_dict=compilation_dict,
            applications=applications,
            leaves={},
            compiler=None,
            insertions=[],
            output_dir=output_dir,
        )

    def set_compiler(self, compiler):
        print("Setting compiler to " + compiler)
        self.compiler = compiler

    def build_dag(self):
        dag = {}
        visited = set()
        parents = []

        for application in self.applications:
            app_node = BuildInfoNode(
                self.compilation_dict[application],
                [],
                [],
                os.path.join(
                    self.output_dir, self.compilation_dict[application].stages[-1].name
                ),
                self.compiler,
            )
            dag[application] = app_node
            visited.add(application)
            parents.append(app_node)

        while len(parents) > 0:
            parent = parents.pop()
            for input in parent.info.inputs:
                if input in visited and input in self.compilation_dict.keys():
                    if parent not in dag[input].outputs:
                        dag[input].outputs.append(parent)
                        parent.inputs.append(dag[input])
                    continue

                visited.add(input)

                if input not in self.compilation_dict.keys():
                    # This is a file we need to grab from the cache, so it is a leaf in the DAG
                    self.leaves[parent.info.output] = parent
                else:
                    # If we previously thought this was a leaf but it has a node child, remove it from leaves
                    self.leaves.pop(parent.info.output, None)

                    child = BuildInfoNode(
                        self.compilation_dict[input],
                        [],
                        [parent],
                        os.path.join(
                            self.output_dir,
                            self.compilation_dict[input].stages[-1].name,
                        ),
                        self.compiler,
                    )
                    dag[input] = child
                    parent.inputs.append(child)
                    parents.append(child)

    def build(self, print_only=False):
        self.build_dag()
        self.apply_insertions()

        visited = []
        frontier = [leaf for _, leaf in self.leaves.items() if leaf.ready()]

        while len(frontier) > 0:
            next_frontier = []
            for node in frontier:
                node.build(print_only)
                visited.append(node)

                for output in node.outputs:
                    if output not in visited and output.ready():
                        next_frontier.append(output)

            frontier = next_frontier

    def insert(self, stage, compiler, name):
        self.insertions.append((stage, compiler, name))

    def apply_insertions(self):
        for stage, compiler, name in self.insertions:
            self.apply_insertion(stage, compiler, name)

    def apply_insertion(self, stage, compiler, name):
        nodes = [leaf for _, leaf in self.leaves.items()]
        while len(nodes) > 0:
            node = nodes.pop()
            if stage in node.info.stages:
                if len(node.info.stages) > 1:
                    # Split node first
                    node = node.split(stage)

                # Make a copy of the current node and then fix the
                # - compiler
                # - stage
                # - output
                # - inputs

                info = copy.copy(node.info)
                info.compiler = compiler
                info.stages = [GCCStage.INSTRUMENT]

                file, _ = os.path.splitext(info.output)
                info.output = name + "_" + file + ".c"  # TODO: don't hardcode this

                instrument_node = BuildInfoNode(
                    info,
                    copy.copy(node.inputs),
                    [node],
                    os.path.join(self.output_dir, info.stages[-1].name),
                    compiler,
                )
                node.inputs = [instrument_node]
                node.info.inputs = [info.output]

                for input in instrument_node.inputs:
                    input.outputs = [instrument_node]

            else:
                nodes.update(node.outputs)
        pass

    def move(self, abs_src, abs_dst):
        rel_src = os.path.normpath(os.path.relpath(abs_src, ROOT_DIR))
        rel_dst = os.path.normpath(os.path.relpath(abs_dst, ROOT_DIR))

        for key, value in self.compilation_dict.items():
            if key == rel_src:
                value["rel_dir"] = os.path.dirname(rel_dst)
                value.output = os.path.basename(rel_dst)
                self.compilation_dict[rel_dst] = value
                del self.compilation_dict[key]
                break
