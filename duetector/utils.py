from datetime import datetime, timedelta

try:
    from functools import cache
except ImportError:
    from functools import lru_cache as cache


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def inet_ntoa(addr) -> bytes:
    dq = b""
    for i in range(0, 4):
        dq = dq + str(addr & 0xFF).encode()
        if i != 3:
            dq = dq + b"."
        addr = addr >> 8
    return dq


@cache
def get_boot_time() -> datetime:
    with open("/proc/stat", "r") as f:
        for line in f:
            if line.startswith("btime"):
                return datetime.fromtimestamp(int(line.split()[1]))
    raise RuntimeError("Could not find btime in /proc/stat")


def get_boot_time_duration_ns(ns) -> datetime:
    ns = int(ns)
    return get_boot_time() + timedelta(microseconds=ns / 1000)


if __name__ == "__main__":
    print(get_boot_time())
    print(get_boot_time_duration_ns("13205215231927"))
