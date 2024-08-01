// -*- c++ -*-
#pragma once

#include <vector>
#include <memory>

#include <lib-utils/dict.h>
#include <lib-utils/rdf-utils.h>

class VisNode;
class VisLink;
class RDFManager;
class VisManager
{
public:
  RDFManager* rdf_man = 0;
  Dict<CURIE, std::shared_ptr<VisNode>> nodes;
  std::vector<std::shared_ptr<VisLink>> links;
  std::string shacl_dump;
  
public:
  VisManager(RDFManager*);

  enum class curie_kind { invalid_curie, valid_curie, valid_curie_dataclass, valid_curie_class };
  curie_kind classify_curie(const CURIE&);

  void build();
  void add_new_userclass();
  void dump_shacl();
  void userclasses_to_triples(std::vector<RDFSPO>* triples_ptr);
  
  void make_frame();
};

