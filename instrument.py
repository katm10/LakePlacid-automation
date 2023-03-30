import argparse
import json
from build_info import BuildInfoDAG, CompilationInfo
from bin.paths import *
from gcc_options import GCCStage


def gen_compilation_info_json():
    compilation_info = {}
    with open(TXT_PATH, "r") as f:
        lines = f.readlines()
        for line in lines:
            info = CompilationInfo.construct(line)

            if info.output is None:
                print(f"WARNING: No output found for command:\n{line}\nSkipping...")
                continue
            if info.output in compilation_info.keys():
                print(f"WARNING: {info.output} already exists! Overwriting...")

            compilation_info[info.output] = info.to_json()

    with open(JSON_PATH, "w") as f:
        json.dump(compilation_info, f, indent=2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "applications", nargs="*", default=None, help="Application(s) to build"
    )
    parser.add_argument("-n", "--no-instrumentation", action="store_true")
    parser.add_argument("-t", "--extract-trace", action="store_true")
    parser.add_argument("-s", "--specialize", action="store_true")
    parser.add_argument("-p", "--print-only", action="store_true")
    args = parser.parse_args()

    # Convert the compilation calls to arg objects
    if not os.path.exists(JSON_PATH):
        gen_compilation_info_json()

    if args.no_instrumentation:
        dag = BuildInfoDAG.construct_from_json(os.path.join(LP_DIR, "uninstrumented"), args.applications)
    elif args.extract_trace:
        dag = BuildInfoDAG.construct_from_json(os.path.join(LP_DIR, "extract_trace"), args.applications)
        dag.set_compiler(
            "/data/commit/graphit/ajaybr/scratch/mpns_clang/build/bin/clang"
        )
        dag.insert(
            GCCStage.COMPILE,
            "/data/commit/graphit/ajaybr/scratch/mpns_clang/build/bin/extract-trace",
            "extract-trace",
        )
    elif args.specialize:
        # TODO: implement this!
        pass
    else:
        print("please specify the type of instrumentation")

    dag.build(args.print_only)


if __name__ == "__main__":
    main()
