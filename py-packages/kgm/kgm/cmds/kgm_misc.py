from .. import graphviz_utils

def do_misc_gv(ttl_file):
    output_png_file = ttl_file + ".png"
    
    g = rdflib.Graph()
    g.parse(ttl_file)
    print("loaded", len(g), "triples")

    #ipdb.set_trace()
    if 'construct_query' in args and not args.construct_query is None:
        with open(args.construct_query) as fd:
            query_text = fd.read()
            print("got query:")
            print(query_text)
            print("---")
            rq_res = g.query(query_text)
            rq_res.graph.namespace_manager = g.namespace_manager # to fix missing namespace bind after construct

            print(f"after contruct: {len(rq_res.graph)} triples")
            #for row in rq_res.graph: print([str(x) for x in row])
            print(f"saving to {output_png_file}")
            graphviz_utils.generate_png(rq_res.graph, png_file = output_png_file)
    else:
        print(f"saving to {output_png_file}")
        graphviz_utils.generate_png(g, png_file = output_png_file)

    print("all done.")        

def do_misc_select(ttl_file):
    g = rdflib.Graph()
    g.parse(ttl_file)
    print("loaded", len(g), "triples")

    with open(args.select_query) as fd:
        query_text = fd.read()
        print("got query:")
        print(query_text)
        print("---")
        rq_res = g.query(query_text)
        ipdb.set_trace()
        #df = pd.DataFrame(columns = [str(x) for x in rq_res.vars], 
        print([str(x) for x in rq_res.vars])
        print("-------")
        for row in rq_res:
            print([str(x) for x in row], len(row))
