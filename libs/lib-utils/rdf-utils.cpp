#include "rdf-utils.h"
#include "uuid.h"

using namespace std;

URI create_classURI(const URI& prefix)
{
  return URI{prefix.uri + "#" + generate_uuid_v4()};
}

std::string get_display_value(const UBOL& l)
{
  string ret;
  if (auto vv = get_if<URI>(&l)) {
    ret = vv->uri;
  } else if (auto vv = get_if<Literal>(&l)) {
    ret = vv->literal;
  } else {
    throw runtime_error("get_display_value failed");
  }
  return ret;
}
