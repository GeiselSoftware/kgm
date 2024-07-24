#!/usr/bin/env python3

import click

from .cmds import kgm_config, kgm_ls, kgm_update, kgm_misc

@click.group()
def cli():
    pass

@cli.command()
def config():
    kgm_config.do_config_show()

@cli.command()
@click.argument("path")
def ls(path):
    print("ls:", path)
    #kgm_ls.do_ls_kgm_graphs()
    kgm_ls.do_ls_all_graphs()
    
    
@cli.command("add")
@click.option("--append", "-a", is_flag = True, help = "append destination graph if exists")
@click.argument("ttl_file")
@click.argument("path")
def do_add(append, ttl_file, path):
    print("do_add:", append, ttl_file, path)
    do_add_graph(ttl_file, path, append)
    
@cli.command()
@click.argument("path")
def rm(path):
    print("rm:", path)

@cli.group("misc")
def do_misc():
    print("misc:")

@do_misc.command("gv")
def do_gv():
    print("gv")
    
def main():
    cli()

