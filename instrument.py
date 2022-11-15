import sys
import argparse
import json
import os
import subprocess
from compilation_info import CompilationInfo
from bin.paths import *

def preprocess(compile_commands):
  compiler = "/data/commit/graphit/ajaybr/scratch/mpns_clang/build/bin/clang" # TODO: seems reasonable to just require clang as a dep?
  input_dir = ROOT_DIR
  output_dir = PREPROCESS_DIR
 
  # with open(os.path.join(BASE_DIR, "name_changes.json")) as f:
  #   name_map = json.load(f)

  for entry in compile_commands:
    command = [compiler]
    command.extend(entry.get_preprocessor_args())
    command.extend(entry.get_unspecified_args())
    command.extend(["-E", f"{input_dir}/{entry.inputs[0]}"])

    print(command)

    with open(os.path.join(output_dir, entry.inputs[0]), "w") as f:
      subprocess.run(command, stdout=f, cwd=output_dir)

def instrument(compile_commands):
  compiler = "/data/commit/graphit/ajaybr/scratch/mpns_clang/build/bin/extract-trace"
  input_dir = os.path.join(SCOUT_DIR, PREPROCESS_DIR)
  output_dir = os.path.join(SCOUT_DIR, INSTRUMENT_DIR)

  for entry in compile_commands:
    command = [compiler, f"{input_dir}/{entry.inputs[0]}", "--"]
    with open(os.path.join(output_dir, entry.inputs[0]), "w") as f:
      subprocess.run(command, stdout=f)

def compile(compile_commands):
  compiler = "/data/commit/graphit/ajaybr/scratch/mpns_clang/build/bin/clang"
  input_dir = os.path.join(SCOUT_DIR, INSTRUMENT_DIR)
  output_dir = os.path.join(SCOUT_DIR, COMPILE_DIR)

  for entry in compile_commands:
    command = [compiler]
    command.extend(entry.get_compiler_args(input_dir))
    command.extend(entry.get_unspecified_args(input_dir))
    command.extend(["-c", f"{input_dir}/{entry.inputs[0]}", "-fPIC", "-o", f"{output_dir}/{entry.output}"])
    
    print(command)
    subprocess.run(command)

def link(linking_commands):
  compiler = "/data/commit/graphit/ajaybr/scratch/mpns_clang/build/bin/clang" # TODO: do we need to use gcc?
  input_dir = os.path.join(SCOUT_DIR, COMPILE_DIR)
  output_dir = os.path.join(SCOUT_DIR, OUTPUT_DIR)

  for entry in linking_commands:
    command = [compiler]
    command.extend(entry.get_linker_args(input_dir))
    command.extend(entry.get_unspecified_args(input_dir))
    command.extend(["-o", f"{output_dir}/{entry.output}"])
    command.extend([f"{input_dir}/{input}" for input in entry.inputs])
    command.extend([os.path.join(LP_DIR, "support", "trace_support.c"), "-lpthread", "-levent"])

    subprocess.Popen(command)
    # print(command)

def main():
  parser = argparse.ArgumentParser()

  parser.add_argument('-p', '--preprocess', action='store_true')
  parser.add_argument('-i', '--instrument', action='store_true')
  parser.add_argument('-c', '--compile', action='store_true')
  parser.add_argument('-l', '--link', action='store_true')
  parser.add_argument('-a', '--all', action='store_true')
  parser.add_argument('-n', '--no-instrumentation', action='store_true')

  args = parser.parse_args()

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

  scouting_dirs = [SCOUT_DIR, PREPROCESS_DIR, INSTRUMENT_DIR, COMPILE_DIR, OUTPUT_DIR]
  for dir in scouting_dirs:
    if not os.path.exists(dir):
      os.mkdir(dir)

  if args.no_instrumentation:
    # TODO: implement me!
    return
  
  if args.preprocess or args.all:
    if not os.path.exists(PREPROCESS_DIR):
      os.mkdir(PREPROCESS_DIR)
    preprocess(compile_commands)
  if args.instrument or args.all:
    if not os.path.exists(INSTRUMENT_DIR):
      os.mkdir(INSTRUMENT_DIR)
    instrument(compile_commands)
  if args.compile or args.all:
    if not os.path.exists(COMPILE_DIR):
      os.mkdir(COMPILE_DIR)
    compile(compile_commands)
  if args.link or args.all:
    if not os.path.exists(OUTPUT_DIR):
      os.mkdir(OUTPUT_DIR)
    link(link_commands)

if __name__ == "__main__":
  main()

