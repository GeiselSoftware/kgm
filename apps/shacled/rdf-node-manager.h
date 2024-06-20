// -*- c++ -*-
#pragma once

#include <set>
#include <vector>
#include <lib-utils/dict.h>
#include <lib-utils/fuseki-utils.h>
#include <lib-utils/http-utils.h>

class VisNode;
class RDFNode
{
public:
  explicit RDFNode();
  explicit RDFNode(const URI& node_uri);
  
  URI node_uri;
  std::set<URI> rdfs_classes;
  std::vector<RDFSPO> triples;
};

class VisNodeManager;
class RDFNodeManager {
private:
  Dict<URI, RDFNode> rdf_nodes;
  Dict<BNode, RDFNode*> bnodes;
  
public:
  void build(const std::vector<RDFSPO>& triples);
  std::shared_ptr<VisNode> create_vis_node(const URI& node_uri);

  void do_dump_shacl();

  HTTPRawRequestHandler http_request_handler; 
  bool in_progress_load_graph_f = false;
  bool in_progress_load_graph() { return this->in_progress_load_graph_f; }
  void start_load_graph(const std::string& gse_path, const std::string& fuseki_server_url);
  bool finish_load_graph(VisNodeManager* vis_node_manager);
};