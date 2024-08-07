#import ipdb
import os
import tempfile
from ..sparql_utils import restore_prefix, rq_construct, rq_select, make_rq

def do_validate(w_config, shacl_kgm_path, kgm_path):
    #ipdb.set_trace()
    print("do_validate:", shacl_kgm_path, kgm_path)
    shacl_g = rq_construct(make_rq(f'construct {{ ?s ?p ?o }} where {{ ?g kgm:path "{shacl_kgm_path}". graph ?g {{?s ?p ?o }} }}'), config = w_config)
    print(len(shacl_g))

    temp_fn = tempfile.mkstemp("shacl.ttl")[1]
    shacl_g.serialize(temp_fn)

    res = rq_select(make_rq(f'select ?g where {{ ?g kgm:path "{kgm_path}" }}'), config = w_config)
    kgm_graph_curie = res.iloc[0, 0]
    kgm_graph_uri = restore_prefix(kgm_graph_curie).toPython()
    print("data graph:", kgm_graph_uri)

    kgm_graph_uri = kgm_graph_uri.replace("#", "%23")
    #validate_curl_cmd = f"curl -s -XPOST --data-binary @{temp_fn}  --header 'Content-type: text/turtle' http://h1:3030/kgm-default-dataset/shacl?graph={kgm_graph_uri}"
    validate_curl_cmd = f"curl -s -XPOST --data-binary @{temp_fn}  --header 'Content-type: text/turtle' {w_config['backend-url']}/shacl?graph={kgm_graph_uri}"
    print(validate_curl_cmd)
    os.system(validate_curl_cmd)
    os.unlink(temp_fn)
    
    print("all done")
