import ipdb
from kgm import Database, KGMGraph

if __name__ == "__main__":
    ipdb.set_trace()
    fuseki_url = "http://localhost:3030/kgm-default-dataset"
    db = Database(fuseki_url)
    kgm_path = "/labpack-test"
    g_uri = db.get_kgm_graph(kgm_path)
    if g_uri is None:
        raise Exception(f"can't find kgm path {kgm_path}")
    g = KGMGraph(db, g_uri)
    ipdb.set_trace()

    uo_uris = g.select_in_current_graph('select ?uo { ?uo :name "test chemical" }').uo
    if len(uo_uris) == 0:
        lp = g.create_user_object(":LabPackChemical")
        lp.State = g.create_user_object(":Solid")
        lp.name = "test chemical"
        lp.Additional_Comments = "this is test entry"
    else:
        lp = g.load_user_object(uo_uris[0])

    if 1:
        un_codes = ["TEST123"]
        un_codes_s = '","'.join(un_codes)
        rq = f'select ?uo {{ ?uo rdf:type :LocalUNCode; :uncode ?uncode. filter(?uncode in ("{un_codes_s}")) }}'
        un_code_uris = g.select_in_current_graph(rq)
        if len(un_code_uris) == 0:
            un_code = g.create_user_object(":LocalUNCode")
            un_code.labpackChemical.add(lp)
            un_code.uncode = "TEST123"
        else:
            un_code = g.load_user_object(un_code_uris.uo[0])

        ipdb.set_trace()
        print(id([x for x in un_code.labpackChemical][0]) == id(lp))
        ipdb.set_trace()
        
    g.save()
