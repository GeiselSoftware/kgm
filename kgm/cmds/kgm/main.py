import click
import importlib.metadata
from kgm.config_utils import get_config
from . import subcmd_toplevel
from . import subcmd_database
from . import subcmd_graph
from . import subcmd_ksd
from . import subcmd_misc

class CustomGroup(click.Group):
    def parse_args(self, ctx, args):
        # If '-h' is in the arguments, replace it with '--help'
        if '-h' in args:
            args[args.index('-h')] = '--help'
        return super().parse_args(ctx, args)

    def format_help(self, ctx, formatter):
        # Add your custom message
        formatter.write(f"kgm version: {importlib.metadata.version('kgm')}\n")
        super().format_help(ctx, formatter)
    
@click.group(cls = CustomGroup)
@click.option("--config", "-c")
@click.option("--verbose", "-v", is_flag = True)
@click.pass_context
def cli(ctx, config, verbose):
    #print("cli pre-subcommand:", config, verbose)
    ctx.ensure_object(dict)
    config_name = 'DEFAULT'
    ctx.obj['config'] = (config_name, get_config(config_name))

cli.add_command(subcmd_toplevel.show_uri)
if 1: # adding graph commands to toplevel
    cli.add_command(subcmd_graph.graph_ls)
    cli.add_command(subcmd_graph.graph_new)
    cli.add_command(subcmd_graph.graph_import)
    cli.add_command(subcmd_graph.graph_remove)
    cli.add_command(subcmd_graph.graph_copy)
    cli.add_command(subcmd_graph.graph_rename)
    
cli.add_command(subcmd_database.database)
cli.add_command(subcmd_graph.graph)
cli.add_command(subcmd_ksd.ksd)
cli.add_command(subcmd_misc.misc)
    
def main():
    cli(max_content_width = 120)
