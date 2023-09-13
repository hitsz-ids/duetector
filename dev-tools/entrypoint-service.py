import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.environ["DUETECTOR_LOG_LEVEL"] = "DEBUG"

import re
import sys
from pathlib import Path

from pkg_resources import load_entry_point

db_file = Path("./duetector-dbcollector.sqlite3")
config_file = Path("./config.toml")

if __name__ == "__main__":
    sys.argv[0] = re.sub(r"(-script\.pyw?|\.exe)?$", "", sys.argv[0])
    sys.argv.append("start")
    sys.argv.extend(["--config", config_file.resolve().as_posix()])
    sys.exit(load_entry_point("duetector", "console_scripts", "duectl-server")())
