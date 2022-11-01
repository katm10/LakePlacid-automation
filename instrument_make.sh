#!/bin/bash

python3 instrumentation/get_args.py $@
gcc $@

