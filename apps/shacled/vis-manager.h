// -*- c++ -*-
#pragma once

#include <vector>
#include <memory>

#include <lib-utils/dict.h>
#include <lib-utils/fuseki-utils.h>

class VisNode;
class VisLink;
class RDFManager;
class VisManager
{
public:  
  Dict<URI, std::shared_ptr<VisNode>> nodes;
  std::vector<std::shared_ptr<VisLink>> links;
  
public:  
  void build(RDFManager*);
  void dump_shacl();
  
  void make_frame();
  std::string shacl_dump;
};

URI expand_curie(const std::string& curie);
std::string asCURIE(const URI&);
