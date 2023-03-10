import argparse
import json
from build_info import BuildInfoDAG, CompilationInfo
from bin.paths import *
from gcc_options import GCCStage

def generate_compilation_info():
  compilation_info = {}
  with open(TXT_PATH, "r") as f:
    lines = f.readlines()
    for line in lines:
      info = CompilationInfo(line)
      if info.output in compilation_info.keys():
        raise Exception(info.output + " already exists")
      
      compilation_info[info.output] = info.to_json()

  with open(JSON_PATH, "w") as f:
    json.dump(compilation_info, f, indent=2)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("applications", nargs="*", default=None, help="Application(s) to build")
  parser.add_argument('-n', '--no-instrumentation', action='store_true')
  parser.add_argument('-t', '--extract-trace', action='store_true')
  parser.add_argument('-s', '--specialize', action='store_true')
  parser.add_argument('-p', '--print-only', action='store_true')
  args = parser.parse_args()

  # Convert the compilation calls to arg objects
  generate_compilation_info()

  if args.no_instrumentation:
    dag = BuildInfoDAG(args.applications, UNMODIFIED_DIR)
  elif args.extract_trace: 
    dag = BuildInfoDAG(args.applications, TRACING_DIR)
    dag.set_compiler("/data/commit/graphit/ajaybr/scratch/mpns_clang/build/bin/clang")
    dag.insert(GCCStage.COMPILE,
            "/data/commit/graphit/ajaybr/scratch/mpns_clang/build/bin/extract-trace",
            "extract-trace")
  elif args.specialize:
    dag = BuildInfoDAG(args.applications, SPECIALIZED_DIR)
    dag.set_compiler("/data/commit/graphit/ajaybr/scratch/mpns_clang/build/bin/clang")
    dag.insert(GCCStage.COMPILE,
            "/data/commit/graphit/ajaybr/scratch/mpns_clang/build/bin/specialize",
            "specialize")
  else:
    print("please specify the type of instrumentation")

  dag.build(args.print_only)

if __name__ == "__main__":
  main()
