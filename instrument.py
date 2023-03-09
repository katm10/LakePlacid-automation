import argparse
from build_info import BuildInfoDAG
from bin.paths import *
from gcc_options import GCCStage

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("applications", nargs="*", default=None, help="Application(s) to build")
  parser.add_argument('-n', '--no-instrumentation', action='store_true')
  parser.add_argument('-t', '--extract-trace', action='store_true')
  parser.add_argument('-s', '--specialize', action='store_true')
  parser.add_argument('-p', '--print-only', action='store_true')
  args = parser.parse_args()


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
