# Expose for plugin system
from .bcc import clone, openat2, tcpconnect
from .sh import uname

registers = [openat2, uname, tcpconnect, clone]
