import click
import importlib.metadata
from .config_utils import get_config
from .database import Database
from .cmds import kgm_graph, kgm_validate, ksd_parser as mod_ksd_parser, kgm_misc

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

@cli.command("show-config")
@click.pass_context
def show_config(ctx):
    w_config_name, w_config = ctx.obj["config"]
    print("current config name:", w_config_name)
    print("current config:", w_config)

@cli.command("ls", help = "lists available graphs")
@click.argument("path", required = False)
@click.pass_context
def graph_ls(ctx, path):
    _, w_config = ctx.obj["config"]
    fuseki_url = w_config['backend-url']
    db = Database(path, fuseki_url)
    kgm_graph.do_ls(db, path)

@cli.command("new", help = "creates new empty graph at given path")
@click.argument("path", required = True)
@click.pass_context
def graph_new(ctx, path):
    _, w_config = ctx.obj["config"]
    fuseki_url = w_config['backend-url']
    db = Database(path, fuseki_url)
    kgm_graph.do_new(db, path)
    
@cli.command("import", help = "import ttl file into the graph")
@click.argument("path", required = True)
@click.argument("ttl_file", required = True)
@click.pass_context
def graph_import(ctx, path, ttl_file):
    _, w_config = ctx.obj["config"]
    fuseki_url = w_config['backend-url']
    db = Database(path, fuseki_url)    
    kgm_graph.do_import(db, path, ttl_file)

@cli.command("cat", help = "prints graph to stdout")
@click.argument("path", required = True)
@click.option("--as-ksd", is_flag = True)
@click.pass_context
def graph_cat(ctx, path, as_ksd):
    _, w_config = ctx.obj["config"]
    fuseki_url = w_config['backend-url']
    db = Database(path, fuseki_url)
    if as_ksd:
        mod_ksd_parser.KSDParser.dump_ksd(db, path)
    else:
        kgm_graph.do_cat(db, path)

@cli.command("show", help = "shows details about given URI")
@click.argument("uri", required = True)
@click.pass_context
def graph_show(ctx, uri):
    _, w_config = ctx.obj["config"]
    fuseki_url = w_config['backend-url']
    db = Database(path, fuseki_url)    
    kgm_graph.do_show(db, uri)
    
@cli.command("remove", help = "removes graph")
@click.argument("path", required = True)
@click.pass_context
def graph_remove(ctx, path):
    _, w_config = ctx.obj["config"]
    fuseki_url = w_config['backend-url']
    db = Database(path, fuseki_url)    
    kgm_graph.do_remove(db, path)

@cli.command("copy", help = "copy graph to new path")
@click.argument("source-path", required = True)
@click.argument("dest-path", required = True)
@click.pass_context
def do_copy(ctx, source_path, dest_path):
    _, w_config = ctx.obj["config"]
    fuseki_url = w_config['backend-url']
    db = Database(path, fuseki_url)    
    kgm_graph.do_copy(db, source_path, dest_path)

@cli.command("rename", help = "changes the path of the graph leaving graph content intact")
@click.argument("path", required = True)
@click.argument("new-path", required = True)
@click.pass_context
def do_rename(ctx, path, new_path):
    _, w_config = ctx.obj["config"]
    fuseki_url = w_config['backend-url']
    db = Database(path, fuseki_url)    
    kgm_graph.do_rename(db, path, new_path)

@cli.command("query")
@click.option("--select-query", "-Q", required = True, help = "select query")
@click.pass_context
def do_graph_select(ctx, select_query):
    _, w_config = ctx.obj["config"]
    fuseki_url = w_config['backend-url']
    db = Database(path, fuseki_url)    
    kgm_graph.do_graph_select(db, select_query)
    
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

@do_misc.command("wasm_test")
def do_misc_wasmtest():
    kgm_misc.do_misc_wasmtest()
    
    
def main():
    cli(max_content_width = 120)
