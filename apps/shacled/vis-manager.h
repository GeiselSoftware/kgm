// -*- c++ -*-
#pragma once

#include <vector>
#include <memory>

#include <lib-utils/dict.h>
#include <lib-utils/rdf-utils.h>

class VisNode;
class VisLink;
class RDFManager;
class VisNode_Class;
class VisNode_UserClass;
class VisNode_DataClass;
class VisManager
{
private:
  friend class VisNode;
  RDFManager* rdf_man = 0;
  std::vector<std::shared_ptr<VisNode>> nodes;
  std::vector<std::shared_ptr<VisLink>> links;

  friend class VisNode_UserClass;
  Dict<CURIE, std::shared_ptr<VisNode_UserClass>> userclasses_by_curie;
  Dict<CURIE, std::shared_ptr<VisNode_DataClass>> dataclasses_by_curie;

public:
  VisManager(RDFManager*);
  void dump_shacl();
  std::string shacl_dump;

  void build();
  void add_new_userclass();
  void userclasses_to_triples(std::vector<RDFSPO>* triples_ptr);

  std::shared_ptr<VisNode_UserClass> find_userclass(const CURIE& curie) { return userclasses_by_curie.get(curie); }
  std::shared_ptr<VisNode_DataClass> find_dataclass(const CURIE& curie) { return dataclasses_by_curie.get(curie); }
  
  void make_frame();
};

