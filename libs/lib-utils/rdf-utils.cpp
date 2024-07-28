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

static std::tuple<std::string, URI> prefixes[] = {
  {rdf::__prefix, rdf::__prefix_uri},
  {rdfs::__prefix, rdfs::__prefix_uri},
  {xsd::__prefix, xsd::__prefix_uri},
  {sh::__prefix, sh::__prefix_uri},

  {kgm::__prefix, kgm::__prefix_uri},
  {ab::__prefix, ab::__prefix_uri},
  {nw::__prefix, nw::__prefix_uri}
};


std::string make_turtle_prefixes(bool is_sparql_style)
{
  ostringstream out;
  string prefix_directive = is_sparql_style ? "prefix" : "@prefix";
  string end_of_line = is_sparql_style ? "\n" : " .\n";
  
  for (auto& [prefix, prefix_uri]: prefixes) {
    out << prefix_directive << " " << prefix << ": " << prefix_uri << end_of_line;
  }
  out << "\n";
  
  return out.str();
}

std::string make_rq(const char* rq)
{
  std::string res = make_turtle_prefixes(true);
  res += rq;
  return res;
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

std::string asCURIE(const URI& uri)
{
  bool found = false;
  std::string ret;
  for (auto& [prefix, prefix_uri]: prefixes) {
    auto idx = uri.uri.find(prefix_uri.uri);
    if (idx == 0) {
      ret = prefix + ":" + uri.uri.substr(idx + prefix_uri.uri.size());
      found = true;
      break;
    }
  }
  
  if (!found) {
    ret = uri.uri;
  }
  
  return ret;
}

URI expand_curie(const std::string& curie)
{
  auto idx = curie.find(":");
  if (idx == std::string::npos) {
    throw std::runtime_error(fmt::format("expand_curie failed: {}", curie));
  }  
  auto curie_prefix = curie.substr(0, idx);

  bool found = false;
  std::string ret;
  for (auto& [prefix, prefix_uri]: prefixes) {
    if (curie_prefix == prefix) {
      ret = prefix_uri.uri + curie.substr(idx + 1);
      found = true;
      break;
    }
  }
  
  if (!found) {
    throw std::runtime_error(fmt::format("can't expand curie {}", curie));
  }
  
  return URI{ret};
}
