import ipdb
import os
import tempfile
from ..sparql_utils import rq_construct, rq_select, make_rq

def do_validate(shacl_kgm_path, kgm_path):
    #ipdb.set_trace()
    print("do_validate:", shacl_kgm_path, kgm_path)
    shacl_g = rq_construct(make_rq(f'construct {{ ?s ?p ?o }} where {{ ?g kgm:path "{shacl_kgm_path}". graph ?g {{?s ?p ?o }} }}'))
    print(len(shacl_g))

    temp_fn = tempfile.mkstemp("shacl.ttl.")[1]
    shacl_g.serialize(temp_fn)

    res = rq_select(make_rq(f'select ?g where {{ ?g kgm:path "{kgm_path}" }}'))
    kgm_graph_uri = res["results"]["bindings"][0]["g"]["value"]
    print("data graph:", kgm_graph_uri)
    
    validate_curl_cmd = f"curl -XPOST --data-binary @{temp_fn}  --header 'Content-type: text/turtle' http://h1:3030/kgm-default-dataset/shacl?graph={kgm_graph_uri}"
    print(validate_curl_cmd)
    os.system(validate_curl_cmd)
    os.unlink(temp_fn)
    
    print("all done")
    
