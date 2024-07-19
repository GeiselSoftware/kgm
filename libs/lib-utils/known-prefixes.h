#pragma once

#include <lib-utils/rdf-utils.h>

struct rdf {
  static inline URI __prefix{"http://www.w3.org/1999/02/22-rdf-syntax-ns#"};
  static inline URI type{__prefix.uri + "type"};
};

struct rdfs {
  static inline URI __prefix{"http://www.w3.org/2000/01/rdf-schema#"};
  static inline URI Class{__prefix.uri + "Class"};
};

struct xsd {
  // using https://www.w3.org/TR/xmlschema-2/#built-in-primitive-datatypes
  static inline URI __prefix{"http://www.w3.org/2001/XMLSchema#"};
  
  static inline URI string{__prefix.uri + "string"};
  static inline URI boolean{__prefix.uri + "boolean"};
  static inline URI decimal{__prefix.uri + "decimal"};
  static inline URI float_{__prefix.uri + "float"};
  static inline URI double_{__prefix.uri + "double"};
  static inline URI duration{__prefix.uri + "duration"};
  static inline URI dateTime{__prefix.uri + "dateTime"};
  static inline URI time{__prefix.uri + "time"};
  static inline URI date{__prefix.uri + "date"};
  static inline URI gYearMonth{__prefix.uri + "gYearMonth"};
  static inline URI gYear{__prefix.uri + "gYear"};
  static inline URI gMonthDay{__prefix.uri + "gMonthDay"};
  static inline URI gDay{__prefix.uri + "gDay"};
  static inline URI gMonth{__prefix.uri + "gMonth"};
  static inline URI hexBinary{__prefix.uri + "hexBinary"};
  static inline URI base64Binary{__prefix.uri + "base64Binary"};

  // from https://www.w3.org/TR/xmlschema-2/#built-in-derived
  static inline URI integer{__prefix.uri + "integer"};
  static inline URI long_{__prefix.uri + "long"};
  static inline URI int_{__prefix.uri + "int"};
  static inline URI short_{__prefix.uri + "short"};
  static inline URI byte_{__prefix.uri + "byte"};
};


struct sh {
  static inline URI __prefix{"http://www.w3.org/ns/shacl#"};
  static inline URI NodeShape{__prefix.uri + "NodeSHAPE"};
  static inline URI property{__prefix.uri + "property"};
  static inline URI path{__prefix.uri + "path"};
  static inline URI class_{__prefix.uri + "class"};
  static inline URI dataclass{__prefix.uri + "dataclass"};
};
