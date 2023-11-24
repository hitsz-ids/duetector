from __future__ import annotations

import os
import threading
from datetime import datetime, timedelta
from pathlib import Path

try:
    from functools import cache
except ImportError:
    from functools import lru_cache as cache

import grpc

from duetector.log import logger


class Singleton(type):
    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
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


@cache
def get_grpc_cred_from_path(
    root_certificates_path: str | Path | None,
    private_key_path: str | Path | None,
    certificate_chain_path: str | Path | None,
) -> grpc.ChannelCredentials:
    def _read_content(path: str | Path | None) -> bytes | None:
        if not path:
            return None
        if isinstance(path, str):
            path = Path(path)
        if not path.exists():
            return None
        with path.open("rb") as f:
            return f.read()

    root_certificates = _read_content(root_certificates_path)
    if not root_certificates:
        # Support GRPC_DEFAULT_SSL_ROOTS_FILE_PATH env
        if "GRPC_DEFAULT_SSL_ROOTS_FILE_PATH" in os.environ:
            logger.debug(
                "Using GRPC_DEFAULT_SSL_ROOTS_FILE_PATH env for root_certificates: %s",
                os.environ["GRPC_DEFAULT_SSL_ROOTS_FILE_PATH"],
            )

            root_certificates = _read_content(os.environ["GRPC_DEFAULT_SSL_ROOTS_FILE_PATH"])

    private_key = _read_content(private_key_path)
    certificate_chain = _read_content(certificate_chain_path)

    logger.debug(
        "root_certificates: %s, private_key: %s, certificate_chain: %s",
        root_certificates,
        private_key,
        certificate_chain,
    )

    return grpc.ssl_channel_credentials(
        root_certificates=root_certificates,
        private_key=private_key,
        certificate_chain=certificate_chain,
    )


if __name__ == "__main__":
    print(get_boot_time())
    print(get_boot_time_duration_ns("13205215231927"))
