import click
import pandas as pd
from kgm.database import Database
from kgm.kgm_utils import get_kgm_graph
from kgm.kgm_graph import KGMGraph

@click.group()
def graph():
    pass

@graph.command("select")
@click.argument("path", required = True)
@click.argument("query", required = True)
@click.pass_context
def do_graph_select(ctx, path, query):
    _, w_config = ctx.obj["config"]
    fuseki_url = w_config['backend-url']
    db = Database(fuseki_url)    
    kgm_g_uri = get_kgm_graph(db, path)
    if kgm_g_uri is None:
        raise Exception(f"can't find kgm path {path}")
    kgm_g = KGMGraph(db, kgm_g_uri, None)
    rq_res = kgm_g.select_in_current_graph(query)
    print(pd.DataFrame(rq_res))
