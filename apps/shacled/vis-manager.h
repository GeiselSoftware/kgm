// -*- c++ -*-
#pragma once

#include <vector>
#include <memory>

#include <lib-utils/dict.h>
#include <lib-utils/fuseki-utils.h>

enum curie_kind { invalid_curie, valid_curie, valid_curie_dataclass, valid_curie_class };

class VisNode;
class VisLink;
class RDFManager;
class VisManager
{
public:
  RDFManager* rdf_man = 0;
  Dict<URI, std::shared_ptr<VisNode>> nodes;
  std::vector<std::shared_ptr<VisLink>> links;
  
public:
  VisManager(RDFManager*);
  curie_kind check_curie(const std::string&);
  static std::string asCURIE(const URI& uri);
  static URI expand_curie(const std::string& curie);

  void build();
  void dump_shacl();
  void userclasses_to_triples(std::vector<RDFSPO>* triples_ptr);
  
  void make_frame();
  std::string shacl_dump;
};

