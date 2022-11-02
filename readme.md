# Automation for LakePlacid

## Setup
1. Replace `CC=gcc` or equivalent in the Makefile with `CC=./instrumentation/run_make.sh`. 
2. Add start and end flags around where each request is processed. TODO: more specificity here.
3. Run make as you would normally to build the application. This will create a `compilation_info.json` file in the `instrumentation` dir. (Note: this is NOT a CompilationDatabase object as specified by clang.)
4. Run `python3 instrumentation/instrument.py <root of application dir>` to instrument the application with the ScoutingCompiler.

## Directory Structure

instrumentation
  |_ compilers/
    |_ extract_trace
    |_ mpns_clang

  |_ scouting/
    |_ preprocessed/
    |_ instrumented/
    |_ compiled/
    |_ output/

## Python Files

IN PROGRESS
compilation_info.py
gcc_options.py

get_args.py
TODO
- not sure how I feel about the dir name
- might change the json obj structure (again...)

get_name_changes.py
TODO
- make this a dropin replacement (idk if this is possible?)

instrument_make.sh - good

instrument.py
TODO
- folder management
- command generation (ie not 100 extends)
- fix intermediates
- can probably abstract this?
- replace input file/dirs with correct paths
