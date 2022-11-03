import sys
import json
import os
import subprocess
from compilation_info import CompilationInfo

BASE_DIR = os.path.abspath(os.path.join( os.path.dirname( __file__ ) ))
SCOUT_DIR = os.path.join(BASE_DIR, "scouting")
PREPROCESS_DIR = os.path.join(SCOUT_DIR, "preprocessed")
INSTRUMENT_DIR = os.path.join(SCOUT_DIR, "instrumented")
COMPILE_DIR = os.path.join(SCOUT_DIR, "compiled")
OUTPUT_DIR = os.path.join(SCOUT_DIR, "output")
JSON_PATH = os.path.join(BASE_DIR, "compilation_info.json")

def preprocess(input_dir, compile_commands):
  compiler = "clang" # os.path.join(BASE_DIR, "compilers", "mpns_clang") # TODO: is there anything special about this compiler?
  input_dir = os.path.abspath(input_dir)
  output_dir = PREPROCESS_DIR
 
  # with open(os.path.join(BASE_DIR, "name_changes.json")) as f:
  #   name_map = json.load(f)

  for entry in compile_commands:
    command = [compiler]
    command.extend(entry.get_preprocessor_args())
    command.extend(entry.get_assembler_args())
    command.extend(entry.get_compiler_args())
    command.extend(entry.get_linker_args())
    command.extend(entry.get_unspecified_args())
    command.extend(["-E", f"{input_dir}/{entry.inputs[0]}"])

    print(command)

    with open(os.path.join(output_dir, entry.inputs[0]), "w") as f:
      subprocess.run(command, stdout=f, cwd=output_dir)

def instrument(compile_commands):
  compiler = "clang" # compiler = os.path.join(BASE_DIR, "compilers", "extract_trace") 
  input_dir = os.path.join(SCOUT_DIR, PREPROCESS_DIR)
  output_dir = os.path.join(SCOUT_DIR, INSTRUMENT_DIR)

  with open(JSON_PATH, "r") as f:
    info = json.load(f)

  for entry in compile_commands:
    command = [compiler, f"{input_dir}/{entry.inputs[0]}", "--"]
    with open(os.path.join(output_dir, entry.inputs[0]), "w") as f:
      subprocess.run(command, stdout=f)

def compile():
  compiler = os.path.join(BASE_DIR, "compilers", "mpns_clang") 
  input_dir = os.path.join(SCOUT_DIR, INSTRUMENT_DIR)
  output_dir = os.path.join(SCOUT_DIR, COMPILE_DIR)

  with open(JSON_PATH, "r") as f:
    info = json.load(f)

  for entry in info["compilation"]:
    command = [compiler]
    command.extend(entry.get_compiler_args())
    command.extend(entry.get_unspecified_args())
    command.extend(["-c", f"{input_dir}/{entry.inputs[0]}", "-fPIC", "-o", f"{output_dir}/{entry.output}"])

    subprocess.run(command)

def link():
  compiler = "gcc" # TODO: do we need to use gcc?
  input_dir = os.path.join(SCOUT_DIR, COMPILE_DIR)
  output_dir = os.path.join(SCOUT_DIR, OUTPUT_DIR)

  with open(JSON_PATH, "r") as f:
    info = json.load(f)

  for entry in info["linking"]:
    command = [compiler]
    command.extend(entry["args"]["linker"])
    command.extend(entry["args"]["unspecified"])
    command.extend(["-o", f"{output_dir}/{entry['output']}"])
    command.extend([f"{input_dir}/{input}" for input in entry["inputs"]])
    command.extend(["support/trace_support.c", "-lpthread", "-levent"])

    subprocess.run(command)

def main():
  if len(sys.argv) < 2:
    print("Usage: python3 instrument.py <source dir>")
    return

  scouting_dirs = [SCOUT_DIR, PREPROCESS_DIR, INSTRUMENT_DIR, COMPILE_DIR, OUTPUT_DIR]
  for dir in scouting_dirs:
    if not os.path.exists(dir):
      os.mkdir(dir)

  compile_commands = []
  link_commands = []
  with open(JSON_PATH, "r") as f:
    info = json.load(f)
    for command in info["compilation"]:
      compilation_info = CompilationInfo()
      compilation_info.from_json(command)
      compile_commands.append(compilation_info)
    for command in info["linking"]:
      compilation_info = CompilationInfo()
      compilation_info.from_json(command)
      link_commands.append(compilation_info)

  source_dir = sys.argv[1]
  preprocess(source_dir, compile_commands)
  instrument(compile_commands)
  # compile()
  # link()

if __name__ == "__main__":
  main()

