#!/usr/bin/env python3

import click
from .cmds import kgm_config, kgm_graph, kgm_validate, kgm_misc

class CustomGroup(click.Group):
    def parse_args(self, ctx, args):
        # If '-h' is in the arguments, replace it with '--help'
        if '-h' in args:
            args[args.index('-h')] = '--help'
        return super().parse_args(ctx, args)
    
@click.group(cls = CustomGroup)
def cli():
    pass

@cli.command()
def config():
    kgm_config.do_config_show()

@cli.group("graph")
def do_graph():
    pass

@do_graph.command()
@click.argument("path")
def ls(path):
    kgm_graph.do_ls_kgm_graphs(path)
    
@do_graph.command("add")
@click.option("--append", "-a", is_flag = True, help = "append destination graph if exists")
@click.option("--kgm-graph-type", type = click.Choice(['data', 'shacl']), default = 'data', show_default = True, help = "KGM graph type, data or shacl")
@click.argument("path")
@click.argument("ttl_file")
def do_add(ttl_file, path, kgm_graph_type, append):
    kgm_graph.do_add_graph(ttl_file, path, kgm_graph_type, append)

@do_graph.command("replace")
@click.argument("path")
@click.argument("ttl_file")
def do_graph_replace(path, ttl_file):
    kgm_graph.do_graph_replace(path, ttl_file)

@do_graph.command("remove")
@click.argument("path")
def rm(path):
    kgm_graph.do_remove_graph(path)

@do_graph.command("query")
@click.option("--select-query-file", required = False, help = "select query file")
@click.option("--select-query", required = False, help = "select query")
def do_graph_select(select_query, select_query_file):
    print(select_query, select_query_file)
    kgm_graph.do_graph_select(select_query, select_query_file)

    
@cli.command("validate")
@click.argument("shacl-path")
@click.argument("path")
def do_validate(shacl_path, path):
    kgm_validate.do_validate(shacl_path, path)
    
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
