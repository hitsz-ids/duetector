import click


@click.command()
def monitor():
    click.echo("Monitoring")


@click.group()
def cli():
    pass


# cli.add_command()
cli.add_command(monitor)

if __name__ == "__main__":
    cli()
