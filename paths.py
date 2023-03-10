import os

ROOT_DIR="${ROOT_DIR}".strip().rstrip('/')
LP_DIR="${LP_DIR}".strip().rstrip('/')
JSON_PATH = os.path.join(LP_DIR, "compilation_info.json")
TXT_PATH = os.path.join(LP_DIR, "compilation_commands.txt")

UNMODIFIED_DIR = os.path.join(LP_DIR, "unmodified")
TRACING_DIR = os.path.join(LP_DIR, "tracing")
SPECIALIZED_DIR = os.path.join(LP_DIR, "specialized")
