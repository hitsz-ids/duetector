import click


@click.command()
def start():
    click.echo("start")


@click.group()
def cli():
    pass


cli.add_command(start)


if __name__ == "__main__":
    cli(["start"])
