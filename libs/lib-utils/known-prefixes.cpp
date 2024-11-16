#include "known-prefixes.h"
#include <vector>
#include <utility>
#include <sstream>

using namespace std;

std::vector<std::tuple<std::string, URI>> prefixes::known_prefixes =
  {
    {rdf::__prefix, rdf::__prefix_uri},
    {rdfs::__prefix, rdfs::__prefix_uri},
    {xsd::__prefix, xsd::__prefix_uri},
    {sh::__prefix, sh::__prefix_uri},    
    {kgm::__prefix, kgm::__prefix_uri},
    {ab::__prefix, ab::__prefix_uri},
    {nw::__prefix, nw::__prefix_uri},
    {__::__prefix, __::__prefix_uri}
  };

bool prefixes::is_good_predicate_prefix(const std::string& s)
{
  return s == rdf::__prefix || s == rdfs::__prefix || s == sh::__prefix
    || s == kgm::__prefix
    || s == ab::__prefix || s == nw::__prefix || s == __::__prefix;
}

std::string prefixes::make_turtle_prefixes(bool is_sparql_style)
{
  ostringstream out;
  string prefix_directive = is_sparql_style ? "prefix" : "@prefix";
  string end_of_line = is_sparql_style ? "\n" : " .\n";
  
  for (auto& [prefix, prefix_uri]: known_prefixes) {
    out << prefix_directive << " " << prefix << ": " << prefix_uri << end_of_line;
  }
  out << prefix_directive << " dummy: <dummy:>" << end_of_line;
  out << "\n";
  
  return out.str();
}

std::string prefixes::make_sparql_query(const char* rq)
{
  std::string res = prefixes::make_turtle_prefixes(true);
  res += rq;
  return res;
}
