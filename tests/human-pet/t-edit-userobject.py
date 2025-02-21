import ipdb
from kgm import Database, KGMGraph

if __name__ == "__main__":
    ipdb.set_trace()
    fuseki_url = "http://localhost:3030/kgm-default-dataset"
    db = Database(fuseki_url)
    g_uris = db.get_graph_uris(["/human-pet", "/human-pet.shacl"])
    g = KGMGraph(db, g_uris[0], g_uris[1:])

    ipdb.set_trace()
    obj_uris = g.select_in_current_graph("select ?uo { ?uo rdf:type :Human }").uo

    obj_uri = obj_uris[0]
    print("obj uri:", obj_uri)
    obj = g.load_user_object(obj_uri)
    print("address:", obj.address)
    obj.address = "2 Main St"
    obj.pet.name = "Bam"
    [x for x in obj.pets][0].name = "Bom"
    
    ipdb.set_trace()
    g.save()
