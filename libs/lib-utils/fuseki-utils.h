// -*- c++ -*-
#pragma once

#include <tuple>
#include <string>
#include <variant>
#include <nlohmann/json.hpp>

//const char* RDF_type = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type";

struct URIRef {
  std::string uri;
};

namespace std {
  template <> struct less<URIRef>
  {
    bool operator() (const URIRef& l, const URIRef& r) const { return l.uri < r.uri; }
  };
}

URIRef create_URI(const URIRef& class_uri);
URIRef create_classURI(const URIRef& prefix);

struct Literal {
  std::string literal;  
};

std::string get_display_value(const std::variant<URIRef, Literal>& l);

inline std::ostream& operator<<(std::ostream& out, const URIRef& obj) { out << "<" << obj.uri << ">"; return out; }
inline std::ostream& operator<<(std::ostream& out, const std::variant<URIRef, Literal> obj) {
  if (obj.index() == 0) {
    out << "<" << std::get<0>(obj).uri << ">";
  } else {
    out << "\"" << std::get<1>(obj).literal << "\"";
  }
  return out;
}

typedef std::tuple<URIRef, URIRef, std::variant<URIRef, Literal>> RDFSPO;
RDFSPO rdf_parse_binding(const nlohmann::json& binding);
