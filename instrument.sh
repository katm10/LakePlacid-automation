#!/usr/bin/env bash

export PATH="/data/commit/graphit/kmohr/workspace/memcached/instrumentation/dropins:$PATH"

rm -rf scouting/
rm compilation_info.json

cd .. 
make clean && make

python3 instrumentation/instrument.py ./

