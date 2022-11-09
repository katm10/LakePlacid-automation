#!/usr/bin/env bash

# Now our dropin replacements for C compilers and mv should be invoked on the first build
export PATH="/data/commit/graphit/kmohr/workspace/memcached/instrumentation/dropins:$PATH"

display_usage() { 
	echo -e "\nUsage: $0 [root directory of application code] \n" 
} 

# if less than two arguments supplied, display usage 
if [  $# -le 1 ] 
then 
  display_usage
  exit 1
fi

export ROOT_DIR=(realpath $1)
export LP_DIR=$ROOT_DIR/instrumentation

# clean up previous instrumentation
rm -rf $LP_DIR/scouting/
rm $LP_DIR/compilation_info.json

# run the initial build to collect the build args
make clean -C $ROOT_DIR 
make -C $ROOT_DIR

# using the build args, run the instrumentation
python3 $LP_DIR/instrument.py $ROOT_DIR 
