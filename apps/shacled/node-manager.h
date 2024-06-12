// -*- c++ -*-
#pragma once

#include <vector>
#include <memory>

class Node;
class Link;
class NodeManager
{
public:  
  std::vector<std::shared_ptr<Node>> nodes;
  std::vector<Link> links;

  std::shared_ptr<Node> create_RDFSClassNode();
  
public:  
  void make_frame();

  void do_dump_shacl();
  void load_json(const char* rq_result);
};
