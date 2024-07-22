#include "rdf-utils.h"

#include "uuid.h"
#include "known-prefixes.h"

using namespace std;

URI create_classURI(const URI& prefix)
{
  return URI{prefix.uri + "#" + generate_uuid_v4()};
}

std::string get_display_value(const RDFPredicate& p)
{
  string ret = asURI(p).uri;
  return ret;
}

std::string get_display_value(const RDFObject& l)
{
  string ret;
  if (auto vv = get_if<URI>(&l)) {
    ret = vv->uri;
  } else if (auto vv = get_if<Literal>(&l)) {
    ret = vv->literal;
  } else if (auto vv = get_if<BNode>(&l)) {
    cout << "runtime_error: " << "get_display_value failed: attempt to display blank node" << endl;
    throw runtime_error("get_display_value failed: attempt to display blank node");
  } else {
    throw runtime_error("get_display_value failed");
  }
  return ret;
}

void URIRep::update(const URI& uri)
{
  this->uri = uri;
  std::tuple<std::string, URI> prefixes[] = {{rdf::__prefix, rdf::__prefix_uri}, {rdfs::__prefix, rdfs::__prefix_uri}, {xsd::__prefix, xsd::__prefix_uri}};
  bool found = false;
  std::string ret;
  for (auto& [prefix, prefix_uri]: prefixes) {
    auto idx = uri.uri.find(prefix_uri.uri);
    if (idx == 0) {
      ret = prefix + ":" + uri.uri.substr(prefix_uri.uri.size());
      found = true;
      break;
    }
  }
    
  if (found) {
    this->uri_rep = ret;
  } else {
    this->uri_rep = uri.uri;
  }
}
