import os

ROOT_DIR="/home/kmohr/Documents/MIT/SuperUROP/workspace/memcached".strip().rstrip('/')
LP_DIR="/home/kmohr/Documents/MIT/SuperUROP/workspace/memcached/instrumentation".strip().rstrip('/')
SCOUT_DIR = os.path.join(LP_DIR, "scouting")
PREPROCESS_DIR = os.path.join(SCOUT_DIR, "preprocessed")
INSTRUMENT_DIR = os.path.join(SCOUT_DIR, "instrumented")
COMPILE_DIR = os.path.join(SCOUT_DIR, "compiled")
OUTPUT_DIR = os.path.join(SCOUT_DIR, "output")
JSON_PATH = os.path.join(LP_DIR, "compilation_info.json")
