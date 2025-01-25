import click
from .ksd_parser import KSDParser

@click.group()
def ksd():
    pass

@ksd.command("dump")
@click.argument("ksd-file", required = True)
@click.pass_context
def do_ksd_dump(ctx, ksd_file):
    ksd_parser = KSDParser()
    ksd_parser.parse_ksd_file(ksd_file)
