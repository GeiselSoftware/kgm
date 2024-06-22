// fuseki:
// download location: https://jena.apache.org/download/index.cgi
// download file: apache-jena-fuseki-5.0.0.tar.gz
// misc:
//   https://jena.apache.org/documentation/fuseki2/fuseki-quick-start.html
//   https://jena.apache.org/documentation/tdb/commands.html#tdbloader
//
// apache-jena-5.0.0/bin/tdbloader --loc ~/local/apache-jena-5.0.0/databases/alice-bob ~/projects/shacled/apps/shacled/alice-bob.ttl
// ./fuseki-server --update --loc=$HOME/local/apache-jena-5.0.0/databases/alice-bob /ds 
//
// example of spaqrl request via http post:
// curl -v -X POST http://h1:3030/ds/ -H "Content-Type: application/x-www-form-urlencoded" -H "Cache-Control: no-cache" -H "Connection: keep-alive" -d query=PREFIX%20rdf%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%3E%0APREFIX%20rdfs%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%3E%0ASELECT%20%2A%20WHERE%20%7B%0A%20%20%3Fsub%20%3Fpred%20%3Fobj%20.%0A%7D%20LIMIT%202
//
//

#include <iostream>
using namespace std;

#include "fuseki-utils.h"

RDFSPPO fuseki::rdf_parse_binding(const nlohmann::json& binding)
{
  /* 
     {
        "s": { "type": "uri", "value": "http://example.com/#alice" },
        "p": { "type": "uri", "value": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type" },
        "o": { "type": "uri", "value": "http://example.com/#Human" }
     }
     ...
     {
        "s": { "type": "uri", "value": "http://example.com/#alice" },
        "p": { "type": "uri", "value": "http://xmlns.com/foaf/0.1/name" },
        "o": { "type": "literal", "value": "Alice" }
     }
  */
  //cout << binding << endl;
  assert(binding["s"]["type"] == "uri" || binding["s"]["type"] == "bnode");
  UOB s;
  if (binding["s"]["type"] == "uri") {
    s = UOB(URI{binding["s"]["value"]});
  } else {
    s = UOB(BNode{binding["s"]["value"]});
  }
  assert(binding["p"]["type"] == "uri");  
  URI p{binding["p"]["value"]};
  //assert(binding["pp"]["type"] == "uri");
  URI pp;
  if (binding.contains("pp")) {
    pp = URI{binding["pp"]["value"]};
  }

  assert(binding["o"]["type"] == "uri" || binding["o"]["type"] == "bnode" || binding["o"]["type"] == "literal");

  UBOL o;
  if (binding["o"]["type"] == "uri") {
    o = UBOL(URI{binding["o"]["value"]});
  } else if (binding["o"]["type"] == "bnode") {
    o = UBOL(BNode{binding["o"]["value"]});
  } else {
    if (binding["o"].contains("datatype")) {
      o = UBOL(Literal{binding["o"]["value"], URI{binding["o"]["datatype"]}});
    } else {
      URI xsd_string_datatype{"http://www.w3.org/2001/XMLSchema#string"};
      o = UBOL(Literal{binding["o"]["value"], xsd_string_datatype});
    }
  }

  return RDFSPPO{s, p, pp, o};
}
