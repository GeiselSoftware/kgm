// -*- c++ -*-
#pragma once

#include <tuple>
#include <string>
#include <variant>
#include <nlohmann/json.hpp>

//const char* RDF_type = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type";

struct URI {
  std::string uri;
};

struct Literal {
  std::string literal;  
  URI datatype;
};

struct BNode {
  std::string bnode;
};

namespace std {
  template <> struct less<URI>
  {
    bool operator() (const URI& l, const URI& r) const { return l.uri < r.uri; }
  };
  
  template <> struct less<BNode>
  {
    bool operator() (const BNode& l, const BNode& r) const { return l.bnode < r.bnode; }
  };
}

typedef std::variant<URI, BNode> UOB; // URI or BNode
typedef std::variant<URI, BNode, Literal> UBOL; // URI, BNode or Literal
std::string get_display_value(const UBOL& l);

inline bool isURI(const UOB& uob) { return uob.index() == 0; }
inline bool isBNode(const UOB& uob) { return uob.index() == 1; }
inline bool isBNode(const UBOL& ubol) { return ubol.index() == 1; }
inline URI asURI(const UOB& uob) { assert(uob.index() == 0); return std::get<0>(uob); }
inline URI asURI(const UBOL& ubol) { assert(ubol.index() == 0); return std::get<0>(ubol); }
inline BNode asBNode(const UOB& uob) { assert(uob.index() == 1); return std::get<1>(uob); }
inline BNode asBNode(const UBOL& ubol) { assert(ubol.index() == 1); return std::get<1>(ubol); }

inline std::ostream& operator<<(std::ostream& out, const URI& uri) { out << "<" << uri.uri << ">"; return out; }
inline std::ostream& operator<<(std::ostream& out, const UOB& uob) {
  if (uob.index() == 0) {
    out << "<" << std::get<0>(uob).uri << ">";
  } else {
    out << std::get<1>(uob).bnode;
  }
  return out;
}

inline std::ostream& operator<<(std::ostream& out, const UBOL ubol) {
  if (ubol.index() == 0) {
    out << "<" << std::get<0>(ubol).uri << ">";
  } else if (ubol.index() == 1) {
    out << std::get<1>(ubol).bnode;
  } else {
    out << "\"" << std::get<2>(ubol).literal << "\"^^<" << std::get<2>(ubol).datatype.uri << ">";
  }
  return out;
}

struct RDFSPO { UOB s; URI p; UBOL o; };
RDFSPO rdf_parse_binding(const nlohmann::json& binding);

URI create_URI(const URI& class_uri);
URI create_classURI(const URI& prefix);
