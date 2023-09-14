#  Modified from https://github.com/Wh1isper/sparglim/blob/0.1.4/sparglim/server/daemon.py
#  Original license:
#    Copyright (c) 2023 Wh1isper
#    Licensed under the BSD 3-Clause License


import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

import psutil

from duetector.log import logger


class Daemon:
    """
    Start a daemon process and record pid.

    Args:
        workdir (str, Path): Working directory for daemon process.
        cmd (List[str]): Command to start daemon process.
        env_dict (Dict[str, str]): Environment variables for daemon process.
        rotate_log (bool): Rotate log file or not.

    Example:
        >>> d = Daemon(
        ...     cmd=["sleep", "100"],
        ...     workdir="/tmp/duetector",
        ...     env_dict={"DUETECTOR_LOG_LEVEL": "DEBUG"},
        ...     auto_restart=True,
        ...     rotate_log=True,
        ... )
        >>> d.start()
        >>> d.poll()
        >>> d.stop()
    """

    def __init__(
        self,
        workdir: Union[str, Path],
        application: str = "daemon",
        cmd: Optional[List[str]] = None,
        env_dict: Optional[Dict[str, str]] = None,
        rotate_log: bool = True,
    ):
        self.cmd: List[str] = cmd or []
        self.workdir: Path = Path(workdir).expanduser().resolve()
        self.workdir.mkdir(parents=True, exist_ok=True)

        self.application: str = application

        self.env_dict: Dict[str, str] = os.environ.copy()
        if env_dict:
            self.env_dict.update(env_dict)

        self.rotate_log: bool = rotate_log

    @property
    def pid_file(self):
        """
        Path to pid file.
        """
        return self.workdir / f"{self.application}.pid"

    @property
    def log_file(self):
        """
        Path to log file.
        """
        return self.workdir / f"{self.application}.log"

    @property
    def pid(self):
        """
        Pid of daemon process.
        """
        if not self.pid_file.exists():
            return None

        with open(self.pid_file) as f:
            return int(f.read())

    def _rotate_log(self):
        """
        Rotate log file.
        """
        now = datetime.now()
        new_log_file = self.log_file.with_name(f"{self.application}-{now:%Y%m%d-%H%M%S}.log")
        logger.info(f"Rotate log file to {new_log_file}")
        self.log_file.rename(new_log_file)

    def start(self):
        """
        Start daemon process.
        """
        if not self.cmd:
            raise RuntimeError("cmd is empty, nothing to start")

        if self.pid:
            logger.error("Daemon is already running, try stop first.")
            return

        if self.rotate_log and self.log_file.exists():
            self._rotate_log()

        p = subprocess.Popen(
            self.cmd,
            cwd=self.workdir.as_posix(),
            env=self.env_dict,
            stdout=self.log_file.open("w"),
            stderr=self.log_file.open("w"),
        )
        logger.info(f"Daemon started, pid: {p.pid}, log: {self.log_file}")
        self.pid_file.write_text(str(p.pid))

        assert self.pid

    def stop(self):
        """
        Stop daemon process.
        """
        if not self.pid:
            return
        pid = self.pid
        try:
            p = psutil.Process(pid)
        except psutil.NoSuchProcess:
            # Already stopped
            pass
        else:
            # We have the process
            try:
                p.terminate()
                logger.info("Wating for daemon to stop")
                p.wait(30)
            except psutil.TimeoutExpired:
                logger.warning("Timeout for terminate daemon, kill it.")
                p.kill()
        self.pid_file.unlink(missing_ok=True)

    def poll(self) -> bool:
        """
        Poll daemon process.
        """
        if not self.pid:
            logger.info("Daemon is not running")
            return False
        try:
            p = psutil.Process(self.pid)
        except psutil.NoSuchProcess:
            logger.info("Daemon is not running but pid file exists, clean pid file")
            self.pid_file.unlink(missing_ok=True)
            return False
        else:
            logger.info(f"Daemon is running, pid: {self.pid}")
            return True


if __name__ == "__main__":
    d = Daemon(
        cmd=["sleep", "100"],
        workdir="/tmp/duetector",
        env_dict={"DUETECTOR_LOG_LEVEL": "DEBUG"},
        auto_restart=True,
        rotate_log=True,
    )
    d.start()
    d.poll()
    d.stop()
