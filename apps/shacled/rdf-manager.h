// -*- c++ -*-
#pragma once

#include <set>
#include <vector>
#include <lib-utils/dict.h>
#include <lib-utils/rdf-utils.h>
#include <lib-utils/http-utils.h>

class RDFManager {
private:
  friend class VisManager;

  std::string fuseki_server_url;  
  
  //Dict<URI, std::vector<URI>> all_user_object_types; // s -> rdf:type -> [o]
  Dict<RDFSubject, Dict<RDFPredicate, std::vector<RDFObject>>> triples; // s -> (p -> [o]), p != rdf:type
  std::set<URI> all_userclasses;
  std::set<URI> all_userobjects;
  
public:
  RDFManager(const std::string& fuseki_server_url);

  CURIE asCURIE(const URI& uri);
  std::pair<URI, bool> expand_curie(const CURIE& curie);
  
  HTTPRawRequestHandler http_request_handler; 
  bool in_progress_load_graph_f = false;
  bool in_progress_load_graph() { return this->in_progress_load_graph_f; }
  void start_load_graph(const std::string& kgm_path);
  bool finish_load_graph();

  bool in_progress_save_graph_f = false;
  void start_save_graph(const std::string& kgm_path, const std::vector<RDFSPO>& triples);
  bool finish_save_graph();
  
  void process_raw_response(const std::string& raw_response);
};
