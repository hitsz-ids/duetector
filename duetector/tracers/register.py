# Expose for plugin system
from . import clone, openat2, tcpconnect, uname

registers = [openat2, uname, tcpconnect, clone]
