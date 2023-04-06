import os
import sys
from dataclasses import dataclass

@dataclass(frozen=True)
class Function:
    name: str
    n: int
    m: int
    branches: dict

@dataclass(frozen=True)
class Manifest:
    command: str
    functions: list

def read_manifest(fname):
    tf = open(fname, "r")
    command = tf.readline().strip()
    

def get_metrics(fname):
    manifest = read_manifest(fname)


def main():
    if len(sys.argv) < 2: 
        print("Usage " + sys.argv[0] + " <filename>")
        exit(1)

    print(get_metrics(sys.argv[1]))

if __name__ == "__main__":
    main()
