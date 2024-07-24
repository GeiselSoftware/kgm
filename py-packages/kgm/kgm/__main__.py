#!/usr/bin/env python3

import sys
#import ipdb
import argparse
import pandas as pd
import rdflib
import uuid

from .sparql_utils import rq_select, rq_insert_graph, rq_update, to_rdfw, kgm_prefix
from . import graphviz_utils

from .cmds import kgm_ls, kgm_misc, kgm_update

def main():
    parser = argparse.ArgumentParser(description="Command processor example")
    subparsers = parser.add_subparsers(title="subcommands") #, description="valid subcommands") #, help="sub-command help")

    if 0:
        subcommand_config = subparsers.add_parser("config", help = "configure graph store explorer")
        subcommand_config_parsers = subcommand_config.add_subparsers()
        subcommand_config_show = subcommand_config_parsers.add_parser("show", help = "shows current config")
        subcommand_config_show.set_defaults(func = do_config_show)
        subcommand_config_set = subcommand_config_parsers.add_parser("set", help = "set specified config_value")
        subcommand_config_set_config_set.add_argument("--key", required = True, help = "key")
        subcommand_config_set.add_argument("--value", required = True, help = "value")
        subcommand_config_set.set_defaults(func = do_config_set)

    if 1:    
        subcommand_graph = subparsers.add_parser("graph", help = "graph commands")
        subcommand_graph_parsers = subcommand_graph.add_subparsers()
        if 1:
            subcommand_show = subcommand_graph_parsers.add_parser("show", help = "shows kgm graphs")
            subcommand_show.set_defaults(func = kgm_ls.do_ls_all_graphs)
        if 1:
            subcommand_upload = subcommand_graph_parsers.add_parser("upload", help = "uploads ttl file")
            subcommand_upload.add_argument("--kgm-path", type=str, required = True, help = "destination kgm graph path")
            subcommand_upload.add_argument("--ttl-file", type=str, required = True, help = "data file")
            subcommand_upload.add_argument("--add", action = 'store_true', required = False, help = "add triples if graph exists")
            subcommand_upload.set_defaults(func = kgm_update.do_upload_graph)            
        if 1:
            subcommand_remove = subcommand_graph_parsers.add_parser("remove", help = "remove kgm graph")
            subcommand_remove.add_argument("--kgm-graph-uri", type=str, required = True, help = "remove KGM graph")
            subcommand_remove.set_defaults(func = kgm_update.do_remove_kgm_graph)
            
    if 0:
        subcommand_remove = subparsers.add_parser("remove", help = "remote kgm graph")
        subcommand_remove.add_argument("--kgm-path", type=str, required = True, help = "kgm graph to remove")
        subcommand_remove.set_defaults(func = kgm_update.do_remove_kgm_graph)

    if 1:
        subcommand_ls = subparsers.add_parser("ls", help = "provides list of all kgm graphs")
        subcommand_ls.set_defaults(func = kgm_ls.do_ls_kgm_graphs)

    if 1:
        subcommand_misc = subparsers.add_parser("misc", help = "misc commands")
        subcommand_misc_parsers = subcommand_misc.add_subparsers()
        if 1:
            subcommand_misc_gv = subcommand_misc_parsers.add_parser("graphviz", help = "graphviz dump to png")
            subcommand_misc_gv.add_argument("--ttl-file", type=str, required = True, help = "ttl file")
            subcommand_misc_gv.add_argument("--construct-query", type=str, required = False, help = "sparql construct query to run before graphviz output")
            subcommand_misc.set_defaults(func = kgm_misc.do_misc_gv)
        if 1:
            subcommand_misc_sparq_select = subcommand_misc_parsers.add_parser("sparql-select", help = "doing select query")
            subcommand_misc_sparq_select.add_argument("--ttl-file", type = str, required = True, help = "ttl file")
            subcommand_misc_sparq_select.add_argument("--select-query", type=str, required = True, help = "sparql select query file")
            subcommand_misc_sparq_select.set_defaults(func = kgm_misc.do_misc_select)            
            
    args = parser.parse_args()
    if 'func' in args:
        args.func(args)
    else:
        parser.print_help()
        
if __name__ == "__main__":
    main()
    
