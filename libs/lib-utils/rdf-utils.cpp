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

RDFSPO::RDFSPO(const RDFSubject& s, const RDFPredicate& p, const RDFObject& o) : s(s), p(p), o(o) {}
RDFSPO::RDFSPO(const URI& s, const URI& p, const URI& o) : s(s), p(p), o(o) {}
RDFSPO::RDFSPO(const URI& s, const URI& p, const Literal& o) : s(s), p(p), o(o) {}
RDFSPO::RDFSPO(const URI& s, const URI& p, const BNode& o) : s(s), p(p), o(o) {}
RDFSPO::RDFSPO(const BNode& s, const URI& p, const URI& o) : s(s), p(p), o(o) {}
RDFSPO::RDFSPO(const BNode& s, const URI& p, const Literal& o) : s(s), p(p), o(o) {}

Literal::Literal(const std::string& literal, const URI& datatype) : literal(literal), datatype(datatype) {}
Literal::Literal(int i) : literal(to_string(i)), datatype(xsd::integer) {}

BNode::BNode() {
  this->bnode = "dummy:" + generate_uuid_v4();
}

BNode::BNode(const std::string& s)
{
  this->bnode = s;
}

bool CURIE::is_good_predicate() const
{
  auto idx = this->curie.find(":");
  if (idx == string::npos) {
    return false;
  }
  auto prefix = this->curie.substr(0, idx);
  return prefixes::is_good_predicate_prefix(prefix);
}

bool CURIE::is_good_userclass_curie() const
{
  auto idx = this->curie.find(":");
  if (idx == string::npos) {
    return false;
  }
  auto prefix = this->curie.substr(0, idx);
  return prefixes::is_good_predicate_prefix(prefix);  
}

//typedef Dict<RDFSubject, Dict<RDFPredicate, std::vector<RDFObject>>> RDFGraph;
void build_rdf_graph(RDFGraph* out, const vector<RDFSPO>& triples)
{
  for (auto& t: triples) {
    auto S = out->get(t.s);
    if (S == 0) {
      S = out->set(t.s);
    }
    
    auto P = S->get(t.p);
    if (P == 0) {
      P = S->set(t.p);
    }

    P->push_back(t.o);
  }
}

void dump_triples(ostream& out, const vector<RDFSPO>& triples)
{
  for (auto& t: triples) {
    out << t.s << " " << t.p << " " << t.o << " .\n";
  }
}

void dump_triples_as_turtle(ostream& out, RDFGraph& g)
{
  for (auto& [s, P]: g) {
    out << s << "\n";
    for (auto& [p, O]: P) {
      out << "   " << p << "\n";
      out << "      ";
      for (int i = 0; i < O.size(); i++) {
	out << O[i];
	if (i + 1 < O.size()) {
	  out << ", ";
	}
      }
      out << ";" << "\n";
    }
    out << "." << "\n";
  }
}

