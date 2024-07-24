def create_uri(rdfs_class):
    uri_s = rdfs_class + "##" + str(uuid.uuid4())
    return rdflib.URIRef(uri_s)

def do_upload_graph(args):
    turtle_file_path = args.ttl_file
    kgm_path = args.kgm_path
    add_f = args.add
    #ipdb.set_trace()

    g = rdflib.Graph()
    g.parse(turtle_file_path, format="turtle")
    
    rq_res = rq_select(f'prefix kgm: <kgm:> select ?s where {{ ?s kgm:path "{kgm_path}" }}')
    print(rq_res)
    if len(rq_res["results"]["bindings"]) in [0, 1]:
        if len(rq_res["results"]["bindings"]) == 1:
            s_uri = rdflib.URIRef(rq_res["results"]["bindings"][0]["s"]["value"])
            if not add_f:
                print(f"graph exists on path {kgm_path}: {s_uri}")
                return
            graph_uri = s_uri
        else:
            graph_uri = create_uri("kgm:Graph")
    else:
        raise Exception(f"path leads to multiple kgm graphs: {rq_res}")

    descr_g = rdflib.Graph()
    descr_g.add((graph_uri, rdflib.URIRef("kgm:path"), rdflib.Literal(kgm_path)))

    rq_insert_graph(descr_g, None)
    rq_insert_graph(g, graph_uri)

    print(kgm_path, graph_uri)
    
def do_remove_kgm_graph(args):
    kgm_graph_uri = args.kgm_graph_uri
    rq_queries = [f"drop graph <{kgm_graph_uri}>",
                  f'delete {{ ?s ?p ?o }} where {{ bind(<{kgm_graph_uri}> as ?s) {{ ?s ?p ?o }} }}']
        
    for rq in rq_queries:
        print(rq)
        rq_update(rq)
