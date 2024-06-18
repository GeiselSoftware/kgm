// -*- c++ -*-
#pragma once

#include <vector>
#include <memory>

#include <lib-utils/fuseki-utils.h>
#include <lib-utils/dict.h>
#include <lib-utils/http-utils.h>

class Node;
class Link;
class NodeManager
{
public:  
  Dict<URIRef, std::shared_ptr<Node>> nodes;
  std::vector<std::shared_ptr<Link>> links;
  
public:  
  void make_frame();

  void do_dump_shacl();

  HTTPRawRequestHandler http_request_handler; 
  bool in_progress_load_graph_f = false;
  bool in_progress_load_graph() { return this->in_progress_load_graph_f; }
  void start_load_graph(const std::string& gse_path, const std::string& fuseki_server_url);
  bool finish_load_graph();
};

