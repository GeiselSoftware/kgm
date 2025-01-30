import click
import pandas as pd
from kgm.database import Database

@click.group("db")
def database():
    pass

@database.command("show-config")
@click.pass_context
def show_config(ctx):
    w_config_name, w_config = ctx.obj["config"]
    print("current config name:", w_config_name)
    print("current config:", w_config)


@database.command("init", help = "initialize server")
@click.option("-r", "--reset", is_flag = True, help = "reset already initialized server")
@click.pass_context
def do_init(ctx, reset):
    _, w_config = ctx.obj["config"]
    fuseki_url = w_config['backend-url']
    db = Database(fuseki_url)
    
    #ipdb.set_trace()
    rq = "select ?s { ?s rdf:type kgm:DefaultServerGraph }"
    rq_res = db.rq_select(rq)

    if len(rq_res["s"]) > 0:
        if not reset:
            raise Exception("kgm init failed: server is already initialized")
        else:            
            print("removing default graph")
            ipdb.set_trace()
            rq = "delete { ?s ?p ?o } where { ?s ?p ?o }"
            db.rq_update(rq)
        
    print("making kgm default graph")

    """
    # this docsstring is for references only
    class kgm:RDFPrefix
      kgm:prefix xsd:string
      kgm:prefix_uri xsd:string
    end

    class kgm:DefaultServerGraph
      kgm:fuseki_dataset_name xsd:string
      kgm:well_known_prefixes kgm:RDFPrefix[6..6]
      kgm:locally_known_prefixes kgm:RDFPrefix[0..n]
    end

    class kgm:Graph
      kgm:path xsd:string
      kgm:dependent_graphs xsd:string[0..n] # dependent graphs idenitied by pathes
    end
    """
    
    ipdb.set_trace()    
    raw_rq = []
    
    raw_rq.append("""\
    kgm:RDFPrefix rdf:type rdfs:Class; rdf:type sh:NodeShape; sh:closed true;
    sh:property [ sh:path kgm:prefix; sh:datatype xsd:string; sh:minCount 1; sh:maxCount 1];
    sh:property [ sh:path kgm:prefix_uri; sh:datatype xsd:string; sh:minCount 1; sh:maxCount 1];
    .
    kgm:DefaultServerGraph rdf:type rdfs:Class; rdf:type sh:NodeShape; sh:closed true;
    sh:property [ sh:path kgm:fuseki_dataset_name; sh:datatype xsd:string; sh:minCount 1; sh:maxCount 1 ];
    sh:property [ sh:path kgm:well_known_prefixes; sh:class kgm:RDFPrefix; sh:minCount 0 ];
    .
    kgm:Graph rdf:type rdfs:Class; rdf:type sh:NodeShape; sh:closed true;
    sh:property [ sh:path kgm:path; sh:datatype xsd:string; sh:minCount 1; sh:maxCount 1];
    .
    """)

    raw_rq.append('kgm:dsg rdf:type kgm:DefaultServerGraph; kgm:fuseki_dataset_name "kgm-default-dataset" .')

    for prefix, prefix_uri in db.prefix_man.well_known_prefixes.items():
        raw_rq.append(f"""\
        kgm:dsg kgm:well_known_prefixes [ 
          rdf:type kgm:RDFPrefix; 
          kgm:prefix "{prefix}"; 
          kgm:prefix_uri "{prefix_uri}"
        ].
        """)        

    raw_rq = "\n".join(raw_rq)
    update_rq = f"""\
    insert data {{
      {raw_rq}
    }}
    """

    ipdb.set_trace()
    db.rq_update(update_rq)    

@database.command("ls", help = "lists available graphs")
@click.argument("path", required = False)
@click.pass_context
def graph_ls(ctx, path):
    _, w_config = ctx.obj["config"]
    fuseki_url = w_config['backend-url']
    db = Database(fuseki_url)

    #print("do_ls:", path)
    query = "select ?kgm_path ?g { ?g rdf:type kgm:Graph; kgm:path ?kgm_path }"
    res = db.rq_select(query)
    print(pd.DataFrame(res).map(lambda x: x.as_turtle()))
