import click
import importlib.metadata
from kgm.config_utils import get_config
from . import kgm_validate, ksd_parser as mod_ksd_parser, kgm_misc
from . import toplevel_cmds

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

cli.add_command(toplevel_cmds.show_config)
cli.add_command(toplevel_cmds.graph_ls)    
cli.add_command(toplevel_cmds.graph_new)
cli.add_command(toplevel_cmds.graph_cat)
cli.add_command(toplevel_cmds.graph_remove)
cli.add_command(toplevel_cmds.graph_rename)
cli.add_command(toplevel_cmds.graph_copy)
cli.add_command(toplevel_cmds.graph_import)
cli.add_command(toplevel_cmds.graph_show)

@cli.command("query")
@click.option("--select-query", "-Q", required = True, help = "select query")
@click.pass_context
def do_graph_select(ctx, select_query):
    _, w_config = ctx.obj["config"]
    fuseki_url = w_config['backend-url']
    db = Database(path, fuseki_url)    
    graph_select__(db, select_query)

def graph_select__(w_config, select_query):
    query_text = make_rq(select_query)

    print("got query:")
    print(query_text)
    print("---")
    rq_res = rq_select(query_text, config = w_config)
    print(rq_res)

    
@cli.command("validate")
@click.argument("shacl-path")
@click.argument("path")
@click.pass_context
def do_validate(ctx, shacl_path, path):
    _, w_config = ctx.obj["config"]
    fuseki_url = w_config['backend-url']
    db = Database(path, fuseki_url)    
    kgm_validate.do_validate(db, shacl_path, path)

@cli.command("ksd")
@click.argument("ksd-file", required = True)
@click.pass_context
def do_ksd_dump(ctx, ksd_file):
    ksd_parser = mod_ksd_parser.KSDParser()
    ksd_parser.parse_ksd_file(ksd_file)

@cli.group("misc")
def do_misc():
    pass

@do_misc.command("graphviz")
@click.option("--ttl-file", required = True, help = "RDF/Turtle file")
@click.option("--construct-rq", help = "construct query file")
def do_misc_graphvis(ttl_file, construct_rq):
    kgm_misc.do_misc_gv(ttl_file, construct_rq)

@do_misc.command("select")
@click.option("--ttl-file", required = True, help = "RDF/Turtle file")
@click.option("--select-query", required = False, help = "select query file")
def do_misc_select(ttl_file, select_query):
    kgm_misc.do_misc_select(ttl_file, select_query)
    
def main():
    cli(max_content_width = 120)
