import sys
import os
from bin.paths import * 

def collect_calls():
  with open(TXT_PATH, "a") as f:
    f.write(" ".join(sys.argv[1:]) + "\n")

if __name__ == "__main__":
  collect_calls()

