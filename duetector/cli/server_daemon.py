import os

import click

from duetector.log import logger
from duetector.tools.daemon import Daemon

WORKDIR_ENV = "DUETECTOR_SERVER_DAEMON_WORKDIR"
DEFAULT_WORKDIR = "/tmp/duetector"
APPLICATION = "duetector-server-daemon"


@click.command(
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
    )
)
@click.option(
    "--workdir",
    default=os.getenv(WORKDIR_ENV, DEFAULT_WORKDIR),
    help="Log file and pid file will be stored in working directory, default: /tmp/duetector",
)
@click.option("--loglevel", default="INFO", help="Log level, default: INFO")
@click.option(
    "--rotate_log",
    default=True,
    help="Rotate log file when process started, default: True",
)
@click.pass_context
def start(ctx, workdir, loglevel, rotate_log):
    """
    Start a background process of command ``duectl-server start``.

    All arguments after ``--`` will be passed to ``duectl-server start``.

    Example:
        ``duectl-server-daemon start -- --config /path/to/config``
    """
    cmd = ["duectl-server", "start"]
    cmd_args = ctx.args
    if cmd_args:
        cmd.extend(cmd_args)
    logger.info(
        f"Start duetector daemon with command: {' '.join(cmd)}, \n"
        f"workdir: {workdir}, \n"
        f"loglevel: {loglevel}, \n"
        f"rotate_log: {rotate_log}"
    )
    Daemon(
        application=APPLICATION,
        cmd=cmd,
        workdir=workdir,
        env_dict={"DUETECTOR_LOG_LEVEL": loglevel},
        rotate_log=rotate_log,
    ).start()


@click.command()
@click.option(
    "--workdir",
    default=os.getenv(WORKDIR_ENV, DEFAULT_WORKDIR),
    help="Log file and pid file will be stored in working directory, default: /tmp/duetector",
)
def status(workdir):
    """
    Show status of process.

    Determined by the existence of pid file in ``workdir``.
    """
    if Daemon(
        workdir=workdir,
        application=APPLICATION,
    ).poll():
        click.echo("Running")
    else:
        click.echo("Stopped")


@click.command()
@click.option(
    "--workdir",
    default=os.getenv(WORKDIR_ENV, DEFAULT_WORKDIR),
    help="Log file and pid file will be stored in working directory, default: /tmp/duetector",
)
def stop(workdir):
    """
    Stop the process.

    Determined by the existence of pid file in ``workdir``.
    """
    Daemon(
        workdir=workdir,
        application=APPLICATION,
    ).stop()
    click.echo("Daemon stopped.")


@click.group()
def cli():
    pass


cli.add_command(start)
cli.add_command(status)
cli.add_command(stop)

if __name__ == "__main__":
    cli(["start"])
