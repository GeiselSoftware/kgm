#pragma once

#include <lib-utils/rdf-utils.h>

struct rdf {
  static inline URI type{"http://www.w3.org/1999/02/22-rdf-syntax-ns#type"};
};

struct rdfs {
  static inline URI Class{"http://www.w3.org/2000/01/rdf-schema#Class"};
};

struct sh {
  static inline URI __prefix{"http://www.w3.org/ns/shacl#"};
  static inline URI NodeShape{__prefix.uri + "NodeSHAPE"};
  static inline URI property{__prefix.uri + "property"};
  static inline URI path{__prefix.uri + "path"};
  static inline URI class_{__prefix.uri + "class"};
  static inline URI dataclass{__prefix.uri + "dataclass"};
};
