import os

ROOT_DIR="${ROOT_DIR}".strip().rstrip('/')
LP_DIR="${LP_DIR}".strip().rstrip('/')
JSON_PATH = os.path.join(LP_DIR, "compilation_info.json")

UNMODIFIED_DIR = os.path.join(LP_DIR, "unmodified")
TRACING_DIR = os.path.join(LP_DIR, "tracing")
SPECIALIZED_DIR = os.path.join(LP_DIR, "specialized")
