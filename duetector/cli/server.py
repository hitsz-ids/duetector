from pathlib import Path

import click
import uvicorn

from duetector.config import CONFIG_PATH, ConfigLoader
from duetector.log import logger
from duetector.service.config import CONFIG_PATH_ENV

SERVER_CONFIG_FILE = "duetector_server_config.toml"
SERVER_ENV_FILE = "duetector_server.env"


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
    "--workdir",
    default=".",
    help=f"Working directory, default: ``.``.",
)
@click.option(
    "--host",
    default="0.0.0.0",
    help=f"Host to listen, default: ``0.0.0.0``.",
)
@click.option(
    "--port",
    default=8120,
    help=f"Port to listen, default: ``8120``.",
)
@click.option(
    "--workers",
    default=1,
    help=f"Number of worker processes, default: ``1``.",
)
def start(config, load_env, workdir, host, port, workers):
    """
    Start duetector server
    """
    config_loader = ConfigLoader(config, load_env=load_env, dump_when_load=False)
    config = config_loader.load_config()
    workdir = Path(workdir).expanduser().resolve()
    server_config_file = workdir / SERVER_CONFIG_FILE
    config_loader.dump_config(config, server_config_file)

    server_env_file = workdir / SERVER_ENV_FILE
    logger.info(f"Init server env file {server_env_file}")
    server_env_file.write_text(f"{CONFIG_PATH_ENV}={server_config_file.absolute().as_posix()}")

    config = uvicorn.Config(
        "duetector.service.app:app",
        host=host,
        port=port,
        workers=workers,
        env_file=SERVER_ENV_FILE,
    )
    server = uvicorn.Server(config)
    server.run()


@click.group()
def cli():
    pass


cli.add_command(start)


if __name__ == "__main__":
    cli(["start"])
