import ipdb
import click
import pandas as pd
from kgm.database import Database
#from kgm.kgm_utils import *
from kgm.kgm_graph import KGMGraph

@click.command("show", help = "shows details about given URI")
@click.argument("uri", required = True)
@click.pass_context
def show_uri(ctx, uri):
    _, w_config = ctx.obj["config"]
    fuseki_url = w_config['backend-url']
    db = Database(fuseki_url)    
    rq = f"""
    select ?uo ?uo_member ?uo_member_value {{ 
      graph ?g
      {{ 
        bind({uri} as ?s_uo)
        ?uo ?uo_member ?uo_member_value .
        ?s_uo (<>|!<>)* ?uo .
      }}
    }}
    """
    #print(rq)

    #ipdb.set_trace()
    rq_res = db.rq_select(rq)
    print(pd.DataFrame(rq_res).map(lambda x: to_turtle(x)))
