// -*- c++ -*-
#include "rdf-node-manager.h"
#include <iostream>

#include <fmt/format.h>
#include <nlohmann/json.hpp>
#include <lib-utils/fuseki-utils.h>

#include "vis-node-data.h"
#include "vis-node-rdfsclass.h"
#include "vis-node-manager.h"

using namespace std;

RDFNode::RDFNode()
{
}

RDFNode::RDFNode(const URI& node_uri)
{
  this->node_uri = node_uri;
}

void RDFNodeManager::build(const vector<RDFSPO>& triples)
{
  for (auto& t: triples) {
    if (isURI(t.s)) {
      auto s = asURI(t.s);
      RDFNode* n = rdf_nodes.get(s);
      if (n == 0) {
	n = rdf_nodes.set(s);
      }

      if (t.p.uri == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type") {
	n->rdfs_classes.insert(asURI(t.o));
      } else {
	n->triples.push_back(t);
	if (isBNode(t.o)) {
	  auto o = asBNode(t.o);
	  if (bnodes.has_key(o)) {
	    throw runtime_error("RDF triples do not for the tree");
	  } else {
	    bnodes.set(o, n);
	  }
	}
      }
    }
  }

  for (auto& t: triples) {
    if (isBNode(t.s)) {
      auto s = asBNode(t.s);
      auto assoc_n = bnodes.get(s);
      if (assoc_n) {
	assoc_n->triples.push_back(t);
      } else {
	throw runtime_error("stray bnode found");
      }
    }
  }
}

shared_ptr<VisNode> RDFNodeManager::create_vis_node(const URI& node_uri)
{
    auto n = this->rdf_nodes.get(node_uri);
    shared_ptr<VisNode> ret;
    if (n->rdfs_classes.contains(URI{"http://www.w3.org/2000/01/rdf-schema#Class"})) {
      ret = make_shared<VisNode_RDFSClass>(node_uri);
      //...;
      
    } else {
      auto lret = make_shared<VisNode_Data>();
      lret->uri = node_uri.uri;
      ret = lret;
    }

    return ret;
}

void RDFNodeManager::do_dump_shacl()
{
  throw runtime_error("not implemented");
#if 0
  cout << "SHACL" << endl;
  for (auto [_, n]: this->nodes) {
    if (auto node = dynamic_pointer_cast<RDFSClassNode>(n); node) {
      cout << "rdfs class " << node->uri << " " << node->label << endl;
      for (auto& m: node->members) {
	cout << m.member_name << ": " << m.member_type << endl;
      }
    } else {
      cout << "unknown node" << endl;
    }
  }

  for (auto link: this->links) {
    cout << "link: " << link->ID.Get() << endl;
  }

  cout << "----" << endl;
#endif
}

void RDFNodeManager::start_load_graph(const string& gse_path, const string& fuseki_server_url)
{
  constexpr auto rq_fmt = R"(prefix gse: <gse:> select ?s ?p ?o {{ ?g gse:path "{}" . graph ?g {{ ?s ?p ?o }} }})";
  
  string rq = fmt::format(rq_fmt, gse_path);
  cout << "sending rq: " << rq << endl;
  decltype(HTTPPostRequest::request_headers) req_headers;
  req_headers.push_back({"Content-Type", "application/x-www-form-urlencoded"});
  //req_headers.push_back({"Accept", "application/n-triples"}); // this is for construct query output selection
  HTTPPostRequest req{fuseki_server_url, req_headers, toUrlEncodedForm(map<string, string>{{"query", rq}})};
  this->http_request_handler.send_http_request(req);
  this->in_progress_load_graph_f = true;
}

bool RDFNodeManager::finish_load_graph(VisNodeManager* vis_node_manager)
{
  string raw_response;
  if (this->http_request_handler.get_response_non_blocking(&raw_response) == false) {
    return false;
  }

  cout << raw_response << endl;
  auto j = nlohmann::json::parse(raw_response);
  vector<RDFSPO> triples;
  for (auto& b: j["results"]["bindings"]) {
    auto spo = rdf_parse_binding(b);
    cout << "finish_load_graph: " << spo.s << " " << spo.p << " " << spo.o << endl;
    triples.push_back(spo);
  }
  this->build(triples);

  for (auto& s: this->rdf_nodes.keys()) {
    auto vn = this->create_vis_node(s);
    vis_node_manager->nodes.set(s, vn);
  }
  
  this->in_progress_load_graph_f = false;
  return true;
}

