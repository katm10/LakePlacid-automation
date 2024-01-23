import os

LP_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(LP_DIR, "compilation_info.json")
TXT_PATH = os.path.join(LP_DIR, "compilation_commands.txt")
ROOT_DIR = os.get_env("ROOT_DIR")