#pragma once

#include <lib-utils/rdf-utils.h>

struct rdf {
  static inline std::string __prefix{"rdf"};
  static inline URI __prefix_uri{"http://www.w3.org/1999/02/22-rdf-syntax-ns#"};
  static inline URI type{__prefix_uri.uri + "type"};
};

struct rdfs {
  static inline std::string __prefix{"rdfs"};
  static inline URI __prefix_uri{"http://www.w3.org/2000/01/rdf-schema#"};
  static inline URI Class{__prefix_uri.uri + "Class"};
};

struct xsd {
  static inline std::string __prefix{"xsd"};
  
  // using https://www.w3.org/TR/xmlschema-2/#built-in-primitive-datatypes
  static inline URI __prefix_uri{"http://www.w3.org/2001/XMLSchema#"};
  
  static inline URI string{__prefix_uri.uri + "string"};
  static inline URI boolean{__prefix_uri.uri + "boolean"};
  static inline URI decimal{__prefix_uri.uri + "decimal"};
  static inline URI float_{__prefix_uri.uri + "float"};
  static inline URI double_{__prefix_uri.uri + "double"};
  static inline URI duration{__prefix_uri.uri + "duration"};
  static inline URI dateTime{__prefix_uri.uri + "dateTime"};
  static inline URI time{__prefix_uri.uri + "time"};
  static inline URI date{__prefix_uri.uri + "date"};
  static inline URI gYearMonth{__prefix_uri.uri + "gYearMonth"};
  static inline URI gYear{__prefix_uri.uri + "gYear"};
  static inline URI gMonthDay{__prefix_uri.uri + "gMonthDay"};
  static inline URI gDay{__prefix_uri.uri + "gDay"};
  static inline URI gMonth{__prefix_uri.uri + "gMonth"};
  static inline URI hexBinary{__prefix_uri.uri + "hexBinary"};
  static inline URI base64Binary{__prefix_uri.uri + "base64Binary"};

  // from https://www.w3.org/TR/xmlschema-2/#built-in-derived
  static inline URI integer{__prefix_uri.uri + "integer"};
  static inline URI long_{__prefix_uri.uri + "long"};
  static inline URI int_{__prefix_uri.uri + "int"};
  static inline URI short_{__prefix_uri.uri + "short"};
  static inline URI byte_{__prefix_uri.uri + "byte"};
};


struct sh {
  static inline std::string __prefix{"sh"};
  static inline URI __prefix_uri{"http://www.w3.org/ns/shacl#"};
  static inline URI NodeShape{__prefix_uri.uri + "NodeShape"};
  static inline URI property{__prefix_uri.uri + "property"};
  static inline URI path{__prefix_uri.uri + "path"};
  static inline URI class_{__prefix_uri.uri + "class"};
  static inline URI dataclass{__prefix_uri.uri + "dataclass"};
  static inline URI minCount{__prefix_uri.uri + "minCount"};
  static inline URI maxCount{__prefix_uri.uri + "maxCount"};
};

struct kgm {
  static inline std::string __prefix{"kgm"};
  static inline URI __prefix_uri{"http://www.geisel-software.com/RDF/KGM#"};
  static inline URI path{__prefix_uri.uri + "path"};
  static inline URI placeholder{__prefix_uri.uri + "placeholder"};
  static inline URI member_name{__prefix_uri.uri + "member_name"};
  static inline URI member_type{__prefix_uri.uri + "member_type"};
};

// example prefixes

struct ab {
  static inline std::string __prefix{"ab"};
  static inline URI __prefix_uri{"http://www.geisel-software.com/RDF/alice-bob#"};
  
};

struct nw {
  static inline std::string __prefix{"nw"};
  static inline URI __prefix_uri{"http://www.geisel-software.com/RDF/NorthWind#"};
};

// ..............................

struct prefixes
{
  static bool is_prefix(const std::string& s);
  static std::vector<std::tuple<std::string, URI>> known_prefixes;
  static std::string make_turtle_prefixes(bool is_sparql_style);
  std::string make_sparql_query(const char* rq);
};
