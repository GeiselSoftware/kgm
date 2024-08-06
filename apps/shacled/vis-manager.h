// -*- c++ -*-
#pragma once

#include <vector>
#include <list>
#include <memory>

#include <lib-utils/dict.h>
#include <lib-utils/rdf-utils.h>

class VisNode;
class VisLink;
class RDFManager;
class VisNode_Class;
class VisNode_UserClass;
class VisNode_DataClass;
class VisManager;

class Action {
protected:
  VisManager* vis_man = 0;

public:
  Action(VisManager* vis_man) { this->vis_man = vis_man; }
  virtual void do_it() = 0;
};

class VisManager
{
private:
  friend class VisNode;
  friend class VisNode_UserClass;
  RDFManager* rdf_man = 0;

  friend class UserClassNode_delete_class;
  friend class UserClassNode_change_class_curie;
  Dict<CURIE, std::shared_ptr<VisNode_Class>> nodes;
  Dict<std::tuple<CURIE, CURIE, CURIE>, std::shared_ptr<VisLink>> links;

  std::list<std::shared_ptr<Action>> pending_actions;
  
public:
  VisManager(RDFManager*);
  void reset();
  std::shared_ptr<VisNode_Class> find_visnode_class(const CURIE& curie);
  void dump_shacl();
  std::string shacl_dump;

  void build_visnode_dataclasses(); 
  void build_visnode_classes();
  void build_userobjects();
  
  void add_new_userclass();
  void userclasses_to_triples(std::vector<RDFSPO>* triples_ptr);
  
  void make_frame();
};

