#include "rdf-utils.h"
#include "uuid.h"
#include "known-prefixes.h"

#include <sstream>
#include <fmt/format.h>

using namespace std;


URI create_classURI(const URI& prefix)
{
  return URI{prefix.uri + "--" + generate_uuid_v4()};
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

