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
  friend class VisNode_UserClass;
  RDFManager* rdf_man = 0;
  std::vector<std::shared_ptr<VisNode>> nodes;
  std::vector<std::shared_ptr<VisLink>> links;

  Dict<CURIE, std::shared_ptr<VisNode_Class>> visnode_classes_by_curie;

public:
  VisManager(RDFManager*);
  void reset();
  std::shared_ptr<VisNode_Class> find_visnode_class(const CURIE& curie);
  void dump_shacl();
  std::string shacl_dump;

  void build_visnode_classes();
  void build_userobjects();
  
  void add_new_userclass();
  void userclasses_to_triples(std::vector<RDFSPO>* triples_ptr);
  
  void make_frame();
};

