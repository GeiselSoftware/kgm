#import ipdb
import os
import tempfile
import pandas as pd

def do_validate(db, shacl_kgm_path, kgm_path):
    #ipdb.set_trace()
    print("do_validate:", shacl_kgm_path, kgm_path)
    shacl_g = db.rq_construct(f'construct {{ ?s ?p ?o }} where {{ ?g kgm:path "{shacl_kgm_path}". graph ?g {{?s ?p ?o }} }}')
    print(len(shacl_g))

    temp_fn = tempfile.mkstemp("shacl.ttl")[1]
    shacl_g.serialize(temp_fn)

    res = pd.DataFrame(db.rq_select(f'select ?g where {{ ?g kgm:path "{kgm_path}" }}'))
    kgm_graph_uri = res.iloc[0, 0]
    print("data graph:", kgm_graph_uri)

    kgm_graph_uri = prefix_man.restore_prefix(kgm_graph_uri.as_turtle()).replace("#", "%23")
    validate_curl_cmd = f"curl -s -XPOST --data-binary @{temp_fn}  --header 'Content-type: text/turtle' {w_config['backend-url']}/shacl?graph={kgm_graph_uri}"
    #print(validate_curl_cmd)
    os.system(validate_curl_cmd)
    os.unlink(temp_fn)
    
    print("all done")
