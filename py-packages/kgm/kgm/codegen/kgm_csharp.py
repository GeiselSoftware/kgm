from ..sparql_utils import make_rq, rq_select

def get_shacl_class_details(kgm_path, w_config):
    rq = make_rq(f"""
    select ?cl ?clm_name ?clm_datatype ?clm_class ?clm_minc ?clm_maxc {{
      ?g kgm:path "{kgm_path}".
      graph ?g {{
       ?cl rdf:type rdfs:Class; sh:property ?cl_prop.
       ?cl_prop sh:path ?clm_name filter(?clm_name != rdfs:type).
       optional {{?cl_prop sh:datatype ?clm_datatype}}
       optional {{?cl_prop sh:class ?clm_class}}
       ?cl_prop sh:minCount ?clm_minc.
       optional {{?cl_prop sh:maxCount ?clm_maxc}}
      }}
    }}
    """)
    print(rq)
    return rq_select(rq, config = w_config)

def generate_csharp_defs(w_config, path):    
    print("generate_csharp_defs:", path)
    print(get_shacl_class_details(path, w_config))
    
    
    
       
