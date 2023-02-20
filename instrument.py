import argparse
import os
from build_info import BuildInfoDAG
from bin.paths import *
from gcc_options import GCCStage

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("applications", nargs="*", default=None, help="Application(s) to build")
  parser.add_argument('-n', '--no-instrumentation', action='store_true')
  parser.add_argument('-p', '--print-only', action='store_true')
  args = parser.parse_args()

  for stage in GCCStage:
    if not os.path.exists(os.path.join(SCOUT_DIR, stage.name)):
      os.makedirs(os.path.join(SCOUT_DIR, stage.name), exist_ok=True)

  dag = BuildInfoDAG(args.applications)

  if args.no_instrumentation:
    print("No instrumentation")
  else: 
    print("Instrumentation being applied")
    dag.set_compiler("/data/commit/graphit/ajaybr/scratch/mpns_clang/build/bin/clang")
    dag.insert(GCCStage.COMPILE, "/data/commit/graphit/ajaybr/scratch/mpns_clang/build/bin/extract-trace")

  dag.build(args.print_only)

if __name__ == "__main__":
  main()


