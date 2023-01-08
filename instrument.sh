#!/usr/bin/env bash

display_usage() { 
	echo -e "\nUsage: $0 [root directory of application code] [package(s) to make, optional] \n" 
} 

# No arguments are supplied, display usage 
if [  $# -lt 1 ] 
then 
  display_usage
  exit 1
fi

export ROOT_DIR=$(realpath $1)
export LP_DIR=$ROOT_DIR/instrumentation
export BIN=$LP_DIR/bin

# Now our dropin replacements for C compilers and mv should be invoked on the first build
OLD_PATH=$PATH
PATH="$LP_DIR/dropins:$PATH"

# clean up previous instrumentation
rm -rf $LP_DIR/scouting/
rm -rf $LP_DIR/bin/
rm $LP_DIR/compilation_info.json

# provide the correct paths to the python files
mkdir -p $BIN
test -f $BIN/paths.py || touch $BIN/paths.py
sed -e s?\$\{ROOT_DIR\}?${ROOT_DIR}?g -e s?\$\{LP_DIR\}?${LP_DIR}?g  ${LP_DIR}/paths.py > ${LP_DIR}/bin/paths.py

# run the initial build to collect the build args
make clean -C $ROOT_DIR 
if [ $# -lt 2 ]; then
  make -C $ROOT_DIR
else
  for i in ${@:2}; do
    make $i -C $ROOT_DIR
  done
fi

# We don't need to instrument the result, so we can remove the dropins
PATH=$OLD_PATH

# using the build args, run the instrumentation
python3 $LP_DIR/instrument.py ${@:2} -p

echo "Done!"

