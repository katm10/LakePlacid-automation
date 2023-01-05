import argparse
import json
import os
import subprocess
from build_info import BuildInfoDAG
from bin.paths import *
from gcc_options import GCCStage

def preprocess(compile_commands):
  compiler = "/data/commit/graphit/ajaybr/scratch/mpns_clang/build/bin/clang" # TODO: seems reasonable to just require clang as a dep?
  input_dir = ROOT_DIR
  output_dir = PREPROCESS_DIR

  for entry in compile_commands:
    input = os.path.join(input_dir, entry.inputs[0])
    if not os.path.exists(input):
        print(f"{input} does not exist")
        pass

    output = os.path.join(output_dir, entry.inputs[0])
    if not os.path.exists(os.path.dirname(output)):
      os.makedirs(os.path.dirname(output), exist_ok=True)

    command = [compiler]
    command.extend(entry.get_preprocessor_args())
    command.extend(entry.get_unspecified_args())
    command.extend(["-E", f"{input}"])

    print(command)

    with open(output, "w") as f:
      subprocess.run(command, stdout=f, cwd=output_dir)

def instrument(compile_commands):
  compiler = "/data/commit/graphit/ajaybr/scratch/mpns_clang/build/bin/extract-trace"
  input_dir = os.path.join(SCOUT_DIR, PREPROCESS_DIR)
  output_dir = os.path.join(SCOUT_DIR, INSTRUMENT_DIR)

  for entry in compile_commands:
    input = os.path.join(input_dir, entry.inputs[0])
    if not os.path.exists(input):
        print(f"{input} does not exist")
        pass
    output = os.path.join(output_dir, entry.inputs[0])
    if not os.path.exists(os.path.dirname(output)):
      os.makedirs(os.path.dirname(output), exist_ok=True)

    command = [compiler, f"{input}", "--"]
    with open(output, "w") as f:
      subprocess.run(command, stdout=f)

def compile(compile_commands):
  compiler = "/data/commit/graphit/ajaybr/scratch/mpns_clang/build/bin/clang"
  input_dir = os.path.join(SCOUT_DIR, INSTRUMENT_DIR)
  output_dir = os.path.join(SCOUT_DIR, COMPILE_DIR)

  for entry in compile_commands:
    input = os.path.join(input_dir, entry.inputs[0])
    if not os.path.exists(input):
        print(f"{input} does not exist")
        pass
    output = os.path.join(output_dir, entry.output)
    if not os.path.exists(os.path.dirname(output)):
      os.makedirs(os.path.dirname(output), exist_ok=True)

    command = [compiler]
    command.extend(entry.get_compiler_args(input_dir))
    command.extend(entry.get_unspecified_args(input_dir))
    command.extend(["-c", f"{input}", "-fPIC", "-o", f"{output}"])
    
    print(command)
    subprocess.run(command)

def link(linking_commands):
  compiler = "/data/commit/graphit/ajaybr/scratch/mpns_clang/build/bin/clang" # TODO: do we need to use gcc?
  input_dir = os.path.join(SCOUT_DIR, COMPILE_DIR)
  output_dir = os.path.join(SCOUT_DIR, OUTPUT_DIR)

  for entry in linking_commands:
    output = os.path.join(output_dir, entry.output)
    if not os.path.exists(os.path.dirname(output)):
      os.makedirs(os.path.dirname(output), exist_ok=True)

    command = [compiler]
    command.extend(entry.get_linker_args(input_dir))
    command.extend(entry.get_unspecified_args(input_dir))
    command.extend(["-o", f"{output}"])
    command.extend([f"{input_dir}/{input}" for input in entry.inputs])
    command.extend([os.path.join(LP_DIR, "support", "trace_support.c"), "-lpthread", "-levent"])

    subprocess.Popen(command)
    # print(command)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("applications", nargs="*", default=None, help="Application(s) to build")
  parser.add_argument('-n', '--no-instrumentation', action='store_true')
  args = parser.parse_args()

  for stage in GCCStage:
    if not os.path.exists(os.path.join(SCOUT_DIR, stage.name)):
      os.makedirs(os.path.join(SCOUT_DIR, stage.name), exist_ok=True)

  dag = BuildInfoDAG(args.applications)

  if args.no_instrumentation:
    print("No instrumentation")
    dag.build()
    return
  else: 
    print("Instrumentation being applied")
    dag.set_compiler("/data/commit/graphit/ajaybr/scratch/mpns_clang/build/bin/clang")
    dag.insert(GCCStage.COMPILE, "/data/commit/graphit/ajaybr/scratch/mpns_clang/build/bin/extract-trace")
    dag.build()

if __name__ == "__main__":
  main()


