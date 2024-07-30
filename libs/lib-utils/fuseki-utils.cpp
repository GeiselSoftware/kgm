// fuseki:
// download location: https://jena.apache.org/download/index.cgi
// download file: apache-jena-fuseki-5.0.0.tar.gz
// misc:
//   https://jena.apache.org/documentation/fuseki2/fuseki-quick-start.html
//   https://jena.apache.org/documentation/tdb/commands.html#tdbloader
//
// example of spaqrl request via http post:
// curl -v -X POST http://h1:3030/kgm-default-dataset/query -H "Content-Type: application/x-www-form-urlencoded" -H "Cache-Control: no-cache" -H "Connection: keep-alive" -d query=select%20*%20%7B%20%3Fs%20%3Fp%20%3Fo%20%7D
//

#include <iostream>
using namespace std;

#include "fuseki-utils.h"

RDFSPO fuseki::rdf_parse_binding(const nlohmann::json& binding)
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
  RDFSubject s;
  if (binding["s"]["type"] == "uri") {
    string uri_string = binding["s"]["value"];
    if (uri_string.find("dummy:") == 0) { // this custom bnode
      s = RDFSubject(BNode("_:" + uri_string.substr(strlen("dummy:"))));
    } else {
      s = RDFSubject(URI{uri_string});
    }
  } else {
    s = RDFSubject(BNode{binding["s"]["value"]});
  }
  assert(binding["p"]["type"] == "uri");  
  RDFPredicate p(URI{binding["p"]["value"]});

  assert(binding["o"]["type"] == "uri" || binding["o"]["type"] == "bnode" || binding["o"]["type"] == "literal");

  RDFObject o;
  if (binding["o"]["type"] == "uri") {
    string uri_string = binding["o"]["value"];
    if (uri_string.find("dummy:") == 0) { // this custom bnode
      o = RDFObject(BNode("_:" + uri_string.substr(strlen("dummy:"))));
    } else {
      o = RDFObject(URI{uri_string});
    }
  } else if (binding["o"]["type"] == "bnode") {
    o = RDFObject(BNode{binding["o"]["value"]});
  } else {
    if (binding["o"].contains("datatype")) {
      o = RDFObject(Literal{binding["o"]["value"], URI{binding["o"]["datatype"]}});
    } else {
      URI xsd_string_datatype{"http://www.w3.org/2001/XMLSchema#string"};
      o = RDFObject(Literal{binding["o"]["value"], xsd_string_datatype});
    }
  }

  return RDFSPO(s, p, o);
}
