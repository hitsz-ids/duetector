import os
import shutil
import signal
import time
from pathlib import Path
from typing import List

import click

from duetector.analyzer.db import DBAnalyzer
from duetector.config import CONFIG_PATH, ConfigLoader
from duetector.log import logger
from duetector.managers.analyzer import AnalyzerManager
from duetector.monitors import BccMonitor, ShMonitor
from duetector.monitors.base import Monitor
from duetector.tools.config_generator import ConfigGenerator


def check_privileges():
    if os.geteuid() != 0:
        raise PermissionError("You need to run this script with sudo or as root.")


@click.command()
@click.option(
    "--load_current_config",
    default=True,
    help=f"Wheather load current config file, if ``True``, will use ``--path`` as origin config file path, default: ``True``.",
)
@click.option(
    "--path",
    default=CONFIG_PATH,
    help=f"Origin config file path, default: ``{CONFIG_PATH}``",
)
@click.option(
    "--load_env",
    default=True,
    help=f"Weather load env variables, "
    f"Prefix: ``{ConfigLoader.ENV_PREFIX}``, Separator:``{ConfigLoader.ENV_SEP}``, "
    f"e.g. ``{ConfigLoader.ENV_PREFIX}config{ConfigLoader.ENV_SEP}a`` means ``config.a``, "
    f"default: ``True``.",
)
@click.option(
    "--dump_path",
    default=CONFIG_PATH,
    help=f"File path to dump, default: ``{CONFIG_PATH}``.",
)
def generate_dynamic_config(load_current_config, path, load_env, dump_path):
    """
    Generate config file of current version, including extensions, modules and env variables
    """
    path = Path(path).expanduser().absolute()

    c = ConfigGenerator(load=load_current_config, path=path, load_env=load_env)
    if path.as_posix() == Path(dump_path).expanduser().absolute().as_posix():
        logger.info(
            f"Dump path is same as origin path, rename {path} to {path.with_suffix('.old')}"
        )
        shutil.move(path, path.with_suffix(".old"))
    c.generate(dump_path)


@click.command()
@click.option(
    "--path",
    default=CONFIG_PATH,
    help=f"Origin config file path, default: ``{CONFIG_PATH}``.",
)
@click.option(
    "--dump_path",
    default=CONFIG_PATH,
    help=f"File path to dump, default: ``{CONFIG_PATH}``.",
)
def make_config(path, dump_path):
    """
    Load config file with env and dump it
    """
    loader = ConfigLoader(path, load_env=True, dump_when_load=False)
    config = loader.load_config()
    shutil.move(loader.config_path, loader.config_path.with_suffix(".old"))
    loader.dump_config(config, dump_path)


@click.command()
@click.option(
    "--path",
    default=CONFIG_PATH,
    help=f"Generated config file path, default: ``{CONFIG_PATH}``.",
)
def generate_config(path):
    """
    Generate config file of current version
    """
    ConfigLoader(path, generate_config=False).generate_config()


@click.command()
@click.option(
    "--config",
    default=CONFIG_PATH,
    help=f"Config file path, default: ``{CONFIG_PATH}``.",
)
@click.option(
    "--load_env",
    default=True,
    help=f"Weather load env variables, "
    f"Prefix: ``{ConfigLoader.ENV_PREFIX}``, Separator:``{ConfigLoader.ENV_SEP}``, "
    f"e.g. ``{ConfigLoader.ENV_PREFIX}config{ConfigLoader.ENV_SEP}a`` means ``config.a``, "
    f"default: True",
)
@click.option(
    "--dump_when_load",
    default=True,
    help=f"Weather dump config when load, default: ``True``.",
)
@click.option(
    "--config_dump_dir",
    default=f"{ConfigLoader.DUMP_DIR}",
    help=f"Config dump dir, default: {ConfigLoader.DUMP_DIR}",
)
@click.option(
    "--enable_bcc_monitor",
    default=True,
    help=f"Set false or False to disable bcc monitor, default: ``True``.",
)
@click.option(
    "--enable_sh_monitor",
    default=True,
    help=f"Set false or False to disable shell monitor, default: ``True``.",
)
@click.option(
    "--brief",
    default=True,
    help=f"Print brief when exit, default: ``True``.",
)
def start(
    config,
    load_env,
    dump_when_load,
    config_dump_dir,
    enable_bcc_monitor,
    enable_sh_monitor,
    brief,
):
    """
    Start A bcc monitor and wait for KeyboardInterrupt
    """

    config = Path(config).expanduser()
    c = ConfigLoader(
        path=config,
        load_env=load_env,
        dump_when_load=dump_when_load,
        config_dump_dir=config_dump_dir,
    ).load_config()
    monitors: List[Monitor] = []
    if enable_bcc_monitor:
        check_privileges()
        monitors.append(BccMonitor(c))
    if enable_sh_monitor:
        monitors.append(ShMonitor(c))

    for m in monitors:
        m.start_polling()

    def _shutdown(sig=None, frame=None):
        logger.info("Exiting...")
        for m in monitors:
            m.shutdown()
        logger.info("All monitors shutdown.")
        if brief:
            try:
                logger.info("Generating brief...")
                analyzers = AnalyzerManager(c).init()
                for a in analyzers:
                    logger.info(str(a.brief(inspect_type=False)))
            except Exception as e:
                logger.error("Exception when generating brief")
                logger.exception(e)
        exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)
    logger.info("Waiting for KeyboardInterrupt or SIGTERM...")
    while True:
        signal.pause()


@click.group()
def cli():
    pass


cli.add_command(start)
cli.add_command(generate_config)
cli.add_command(make_config)
cli.add_command(generate_dynamic_config)

if __name__ == "__main__":
    cli(["start"])
