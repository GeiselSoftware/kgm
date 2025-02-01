from .rdf_terms import URI

class CURIE:
    def __init__(self, curie_prefix:str, curie_suffix:str):
        self.curie_prefix = curie_prefix
        self.curie_suffix = curie_suffix

    @staticmethod
    def parse(self, curie_str:str) -> "CURIE":
        return CURIE(curie_str.split(":"))

class PrefixManager:
    def __init__(self):
        self.is_initialized = False
        self.prefixes = {} # prefix -> prefix_uri

    def init(self, db:"Database", g:URI):
        for prefix, prefix_uri in db.well_known_prefixes.items():
            self.prefixes[prefix] = URI(prefix_uri)
        self.prefixes[""] = URI(g.uri + "#")
        self.is_initialized = True
        
    def collapse_prefix(self, uri:str) -> str:
        assert(self.is_initialized)
        assert(type(uri) == str)
        for p, p_uri in self.prefixes.items():
            #print(uri, p_uri)
            if uri.find(p_uri) == 0:
                return uri.replace(p_uri, p + ":")
        raise Exception("can't collapse prefix for URI:", uri)

    def restore_prefix(self, curie:str) -> URI:
        assert(self.is_initialized)
        assert(type(curie) == str)
        for prefix, prefix_uri in self.prefixes.items():
            if curie.find(prefix) == 0:
                return URI(curie.replace(prefix + ":", prefix_uri.uri))
        raise Exception("can't restore prefix in curie", curie)

    def to_rdfw__(self, d):
        assert(self.is_initialized)
        if pd.isnull(d):
            return None
        if d['type'] == 'uri':
            return URI(self.collapse_prefix(d['value']))
        if d['type'] == 'literal':
            if not 'datatype' in d:
                datatype = xsd.string
            else:
                datatype = URI(self.collapse_prefix(d['datatype']))
            return Literal(d['value'], datatype)
        if d['type'] == 'bnode':
            return BNode(d['value'])
        raise Exception("unknown type")
