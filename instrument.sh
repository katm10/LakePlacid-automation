#!/usr/bin/env bash

export ROOT_DIR=$(realpath $1)
export LP_DIR=$ROOT_DIR/instrumentation
export BIN=$LP_DIR/bin

# Now our dropin replacements for C compilers and mv should be invoked on the first build
PATH="$LP_DIR/dropins:$PATH"

display_usage() { 
	echo -e "\nUsage: $0 [root directory of application code] [package to make] \n" 
} 

# if less than two arguments supplied, display usage 
if [  $# -ne 2 ] 
then 
  display_usage
  exit 1
fi

# clean up previous instrumentation
rm -rf $LP_DIR/scouting/
rm -rf $LP_DIR/bin/
rm $LP_DIR/compilation_info.json

# provide the correct paths to the python files
mkdir -p $BIN
test -f $BIN/paths.py || touch $BIN/paths.py
sed -e s?\$\{ROOT_DIR\}?${ROOT_DIR}?g -e s?\$\{LP_DIR\}?${LP_DIR}?g  ${LP_DIR}/paths.py > ${LP_DIR}/bin/paths.py

# # run the initial build to collect the build args
make clean -C $ROOT_DIR 
make $2 -C $ROOT_DIR

# using the build args, run the instrumentation
python3 $LP_DIR/instrument.py -a

echo "Done!"

