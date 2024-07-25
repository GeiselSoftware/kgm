#!/usr/bin/env python3

import click
from .cmds import kgm_config, kgm_ls, kgm_update, kgm_misc

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

@cli.command()
@click.argument("path")
def ls(path):
    kgm_ls.do_ls_kgm_graphs(path)
    #kgm_ls.do_ls_all_graphs()
    
    
@cli.command("add")
@click.option("--append", "-a", is_flag = True, help = "append destination graph if exists")
@click.option("--kgm-graph-type", help = "KGM graph type, data or shacl")
@click.argument("ttl_file")
@click.argument("path")
def do_add(ttl_file, path, kgm_graph_type, append):
    kgm_update.do_add_graph(ttl_file, path, kgm_graph_type, append)
    
@cli.command()
@click.argument("path")
def rm(path):
    kgm_update.do_remove_graph(path)

@cli.group("misc")
def do_misc():
    print("misc:")

@do_misc.command("graphviz")
@click.option("--ttl-file", help = "RDF/Turtle file")
@click.option("--construct-rq", required = False, help = "construct query file")
def do_misc_graphvis(ttl_file, construct_rq):
    kgm_misc.do_misc_gv(ttl_file, construct_rq)

@do_misc.command("select")
@click.option("--ttl-file", required = True, help = "RDF/Turtle file")
@click.option("--select-query", required = False, help = "construct query file")
def do_misc_select(ttl_file, select_query):
    kgm_misc.do_misc_select(ttl_file, select_query)
    
def main():
    cli()

