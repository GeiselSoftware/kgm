// -*- c++ -*-
#pragma once

#include <vector>
#include <memory>

#include <lib-utils/fuseki-utils.h>
#include <lib-utils/dict.h>

class Node;
class Link;
class NodeManager
{
public:  
  Dict<URIRef, std::shared_ptr<Node>> nodes;
  std::vector<Link> links;
  
public:  
  void make_frame();

  void do_dump_shacl();
  void load_json(const char* rq_result);
};

