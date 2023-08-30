import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

import re
import sys

from pkg_resources import load_entry_point

if __name__ == "__main__":
    os.unlink("./duetector-dbcollector.sqlite3")
    sys.argv[0] = re.sub(r"(-script\.pyw?|\.exe)?$", "", sys.argv[0])
    sys.argv.append("start")
    sys.argv.extend(["--config", "./config.toml"])
    sys.exit(load_entry_point("duetector", "console_scripts", "duectl")())
