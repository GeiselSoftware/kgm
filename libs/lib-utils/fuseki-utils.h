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

namespace std {
  template <> struct less<URI>
  {
    bool operator() (const URI& l, const URI& r) const { return l.uri < r.uri; }
  };
}

URI create_URI(const URI& class_uri);
URI create_classURI(const URI& prefix);

struct Literal {
  std::string literal;  
};

typedef std::variant<URI, Literal> UOL; // URI or Literal
std::string get_display_value(const UOL& l);

inline std::ostream& operator<<(std::ostream& out, const URI& uri) { out << "<" << uri.uri << ">"; return out; }
inline std::ostream& operator<<(std::ostream& out, const UOL uol) {
  if (uol.index() == 0) {
    out << "<" << std::get<0>(uol).uri << ">";
  } else {
    out << "\"" << std::get<1>(uol).literal << "\"";
  }
  return out;
}

typedef std::tuple<URI, URI, UOL> RDFSPO;
typedef std::map<Literal, UOL> aux_output_t;
RDFSPO rdf_parse_binding(const nlohmann::json& binding, aux_output_t* aux_output);
