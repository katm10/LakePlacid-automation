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

# define the paths to the instrumentation files
export ROOT_DIR=$(realpath $src)
export LP_DIR=$ROOT_DIR/instrumentation
export JSON_PATH=$LP_DIR/compilation_info.json
export TXT_PATH=$LP_DIR/compilation_commands.txt
export BIN=$LP_DIR/bin

# clean up previous instrumentation
rm -rf $LP_DIR/scouting/
rm -rf $LP_DIR/modified/
rm -rf $LP_DIR/bin/

# Provide the correct paths to the python files and generate dropins for the C compilers
mkdir $BIN
test -f $BIN/paths.py || touch $BIN/paths.py
for path in ROOT_DIR LP_DIR JSON_PATH TXT_PATH BIN; do
  echo "${path}=\"${!path}\".strip().rstrip('/')" >> $BIN/paths.py
done

mkdir $BIN/dropins
for compiler in gcc cc clang tcc; do
  original=$(which $compiler)
  if [ -z "$original" ]; then
    echo "Could not find $compiler, skipping"
    continue
  fi
  test -f $BIN/dropins/$compiler || touch $BIN/dropins/$compiler
  sed -e s?\$\{COMPILER\}?$compiler?g -e s?\$\{ORIGINAL\}?${original}?g  ${LP_DIR}/dropin_template > ${LP_DIR}/bin/dropins/$compiler
  chmod +x ${LP_DIR}/bin/dropins/$compiler
done


# run the initial build to collect the build args
if [ $make_compilationinfo = true ]; then
  # clean up previous compilation info
  rm $LP_DIR/compilation_commands.txt
  rm $LP_DIR/compilation_info.json
  make clean -C $ROOT_DIR 

  # our dropin replacements for C compilers and mv should be invoked on the first build
  OLD_PATH=$PATH
  PATH="$LP_DIR/bin/dropins:$PATH"

  if [ ${#apps[@]} -eq 0 ]; then
    make -C $ROOT_DIR
  else
    for app in "${apps[@]}"; do
      make $app -C $ROOT_DIR
    done
  fi

  # We don't need to instrument the result, so we can remove the dropins
  PATH=$OLD_PATH
fi

# using the build args, run the instrumentation
python3 $LP_DIR/instrument.py ${apps[@]} -t $flags

echo "Done!"

