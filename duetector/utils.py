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
