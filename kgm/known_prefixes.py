from .rdf_terms import URI

def build_uri__(prefix_cls, suffix):
    return URI(prefix_cls.prefix_uri__ + suffix)

class rdf:
    prefix__ = "rdf"
    prefix_uri__ = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"

rdf.type = build_uri__(rdf, "type")

class rdfs:
    prefix__ = "rdfs"
    prefix_uri__ = "http://www.w3.org/2000/01/rdf-schema#"
    
rdfs.Class = build_uri__(rdfs, "Class")
    
class xsd:
    prefix__ = "xsd"
    prefix_uri__ = "http://www.w3.org/2001/XMLSchema#"

xsd.string = build_uri__(xsd, "string")
xsd.boolean = build_uri__(xsd, "boolean")
xsd.integer = build_uri__(xsd, "integer")
xsd.float = build_uri__(xsd, "float")
xsd.double = build_uri__(xsd, "double")

xsd_dflt_cs_values = {}
xsd_dflt_cs_values[xsd.string] = "\"\""
xsd_dflt_cs_values[xsd.boolean] = "\"false\""
xsd_dflt_cs_values[xsd.integer] = "0"
xsd_dflt_cs_values[xsd.float] = "0.0f"
xsd_dflt_cs_values[xsd.double] = "0.0"

class sh:
    prefix__ = "sh"
    prefix_uri__ = "http://www.w3.org/ns/shacl#"

sh.property = build_uri__(sh, "property")
sh.path = build_uri__(sh, "path")
sh.datatype = build_uri__(sh, "datatype")
sh.class_ = build_uri__(sh, "class")
sh.min_c = build_uri__(sh, "minCount")
sh.max_c = build_uri__(sh, "maxCount")
sh.NodeShape = build_uri__(sh, "NodeShape")

class dash:
    prefix__ = "dash"
    prefix_uri__ = "http://datashapes.org/dash#"

dash.closedByType = build_uri__(dash, "closedByType")

class kgm:
    prefix__ = "kgm"
    prefix_uri__ = "http://www.geisel-software.com/kgm/kgm#"

kgm.Graph = build_uri__(kgm, "Graph")
kgm.path = build_uri__(kgm, "path")

well_known_prefixes = {
    rdf.prefix__: rdf.prefix_uri__,
    rdfs.prefix__: rdfs.prefix_uri__,
    xsd.prefix__: xsd.prefix_uri__,
    sh.prefix__: sh.prefix_uri__,
    dash.prefix__: dash.prefix_uri__,
    kgm.prefix__: kgm.prefix_uri__,
}
