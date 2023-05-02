import sys
from trace_helpers import read_trace_dir


def main():
    if len(sys.argv) < 2:
        print("Usage " + sys.argv[0] + " <filename>")
        exit(1)

    _, functions = read_trace_dir(sys.argv[1])
    for f in functions:
        print(f)


if __name__ == "__main__":
    main()
