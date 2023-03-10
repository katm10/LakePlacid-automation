#!/usr/bin/env bash

flags=''
make_compilationinfo=false
apps=()
src=''

while getopts "npmo:" flag; do
  case "${flag}" in
    n) flags+=' -n';;
    p) flags+=' -p';;
    m) make_compilationinfo=true;;
    o) apps+=("${OPTARG}");;
    *) exit 1;;
  esac
done

shift $((OPTIND-1))

if [[ $# -gt 0 ]]; then
  src=$1
  shift
fi

for arg in "$@"; do
  if [[ $arg != -* ]]; then
    apps+=("$arg")
  fi
done

display_usage() { 
	echo -e "\nUsage: $0 [-n] [-p] [-m] [-o app] [root directory of application code] \n"
  echo "  -n   disable instrumentation"
  echo "  -p   print only, do not run the generated commands"
  echo "  -m   re-make the source code, generating a new compilation_info.json"
  exit 1
} 

# The src directory was not specified, display the usage
if [ -z "$src" ]; then
  display_usage
fi

export ROOT_DIR=$(realpath $src)
export LP_DIR=$ROOT_DIR/instrumentation
export BIN=$LP_DIR/bin

# Now our dropin replacements for C compilers and mv should be invoked on the first build
OLD_PATH=$PATH
PATH="$LP_DIR/dropins:$PATH"

# clean up previous instrumentation
rm -rf $LP_DIR/scouting/
rm -rf $LP_DIR/modified/
rm -rf $LP_DIR/bin/

if [ $make_compilationinfo = true ]; then
  rm $LP_DIR/compilation_commands.txt
  rm $LP_DIR/compilation_info.json
fi

# provide the correct paths to the python files
mkdir -p $BIN
test -f $BIN/paths.py || touch $BIN/paths.py
sed -e s?\$\{ROOT_DIR\}?${ROOT_DIR}?g -e s?\$\{LP_DIR\}?${LP_DIR}?g  ${LP_DIR}/paths.py > ${LP_DIR}/bin/paths.py

# run the initial build to collect the build args
if [ $make_compilationinfo = true ]; then
  make clean -C $ROOT_DIR 
  if [ ${#apps[@]} -eq 0 ]; then
    make -C $ROOT_DIR
  else
    for app in "${apps[@]}"; do
      make $app -C $ROOT_DIR
    done
  fi
fi

# We don't need to instrument the result, so we can remove the dropins
PATH=$OLD_PATH

# using the build args, run the instrumentation
python3 $LP_DIR/instrument.py ${apps[@]} -t $flags

echo "Done!"

