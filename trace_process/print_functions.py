import read_trace
import sys
import os


def main():
    if len(sys.argv) < 2:
        print("Usage " + sys.argv[0] + " <filename>")
        exit(1)

    functions = read_trace.read_trace_dir_old(sys.argv[1])["functions"]
    for f in functions:
        print(f)


if __name__ == "__main__":
    main()
