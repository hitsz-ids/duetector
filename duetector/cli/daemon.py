import click


@click.command()
def start():
    """
    Start daemon
    """
    pass


@click.command()
def status():
    """
    Status of daemon
    Determined by the existence of pid file in `workdir`
    """
    pass


@click.command()
def stop():
    """
    Stop daemon
    """
    pass


@click.group()
def cli():
    pass


cli.add_command(start)
cli.add_command(status)
cli.add_command(stop)

if __name__ == "__main__":
    cli(["start"])
