import os
import shutil
import time
from pathlib import Path

import click

from duetector.config import CONFIG_PATH, ConfigLoader
from duetector.monitors import BccMonitor
from duetector.tools.config_generator import ConfigGenerator


def check_privileges():
    if os.geteuid() != 0:
        raise PermissionError("You need to run this script with sudo or as root.")


@click.command()
@click.option(
    "--load_current_config",
    default=True,
    help=f"Wheather load current config file, if True, will use --path as origin config file path, default True.",
)
@click.option(
    "--path",
    default=CONFIG_PATH,
    help=f"Origin config file path, default: {CONFIG_PATH}",
)
@click.option(
    "--load_env",
    default=True,
    help=f"Weather load env variables when load current config, default True, Prefix: {ConfigLoader.ENV_PREFIX}, Separator:{ConfigLoader.ENV_SEP}, eg. {ConfigLoader.ENV_PREFIX}config{ConfigLoader.ENV_SEP}a means config.a",
)
@click.option(
    "--dump_path",
    default=CONFIG_PATH,
    help=f"File path to dump, default: {CONFIG_PATH}",
)
def generate_dynamic_config(load_current_config, path, load_env, dump_path):
    """
    Generate config file of current version, including extensions, modules and env variables
    """
    path = Path(path).expanduser().absolute()

    c = ConfigGenerator(load=load_current_config, path=path, load_env=load_env)
    if path.as_posix() == Path(dump_path).expanduser().absolute().as_posix():
        shutil.move(path, path.with_suffix(".old"))
    c.generate(dump_path)


@click.command()
@click.option(
    "--path",
    default=CONFIG_PATH,
    help=f"Origin config file path, default: {CONFIG_PATH}",
)
@click.option(
    "--dump_path",
    default=CONFIG_PATH,
    help=f"File path to dump, default: {CONFIG_PATH}",
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
    help=f"Generated config file path, default: {CONFIG_PATH}",
)
def generate_config(path):
    """
    Generate config file of current version
    """
    ConfigLoader(path, generate_config=False).generate_config()


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
    """
    Start A bcc monitor and wait for KeyboardInterrupt
    """

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
cli.add_command(make_config)
cli.add_command(generate_dynamic_config)

if __name__ == "__main__":
    cli(["start"])
