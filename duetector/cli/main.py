import os
import time
from pathlib import Path

import click

from duetector.config import CONFIG_PATH, ConfigLoader
from duetector.monitors import BccMonitor


def check_privileges():
    if os.geteuid() != 0:
        raise PermissionError("You need to run this script with sudo or as root.")


@click.command()
@click.option(
    "--path",
    default=CONFIG_PATH,
    help=f"Generated config file path, default: {CONFIG_PATH}",
)
@click.option(
    "--load_env",
    default=True,
    help=f"Weather load env variables, Prefix: {ConfigLoader.ENV_PREFIX}, Separator:{ConfigLoader.ENV_SEP}, eg. {ConfigLoader.ENV_PREFIX}config{ConfigLoader.ENV_SEP}a means config.a",
)
def generate_config(path):
    """
    Generate config file of current version
    """
    ConfigLoader(path).generate_config()


@click.command()
@click.option("--config", default=CONFIG_PATH, help=f"Config file path, default: {CONFIG_PATH}")
@click.option(
    "--load_env",
    default=True,
    help=f"Weather load env variables, Prefix: {ConfigLoader.ENV_PREFIX}, Separator:{ConfigLoader.ENV_SEP}, eg. {ConfigLoader.ENV_PREFIX}config{ConfigLoader.ENV_SEP}a means config.a",
)
@click.option(
    "--dump_when_load",
    default=True,
    help=f"Weather dump config when load, default: True",
)
@click.option(
    "--config_dump_dir",
    default=f"{ConfigLoader.DUMP_DIR}",
    help=f"Config dump dir, default: {ConfigLoader.DUMP_DIR}",
)
def start(config, load_env, dump_when_load, config_dump_dir):
    check_privileges()
    config = Path(config).expanduser()
    c = ConfigLoader(
        path=config,
        load_env=load_env,
        dump_when_load=dump_when_load,
        config_dump_dir=config_dump_dir,
    ).load_config()
    m = BccMonitor(c)

    while True:
        try:
            time.sleep(0.5)
            m.poll_all()
        except KeyboardInterrupt:
            print(m.summary())
            exit()


@click.group()
def cli():
    pass


cli.add_command(start)
cli.add_command(generate_config)

if __name__ == "__main__":
    cli(["start"])
