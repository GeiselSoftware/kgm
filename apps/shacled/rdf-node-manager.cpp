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

void RDFNodeManager::build_rdf_nodes(const std::string& raw_response)
{
  auto j = nlohmann::json::parse(raw_response);

#if 0
  vector<RDFSPO> triples;
  for (auto& b: j["results"]["bindings"]) {
    auto spo = rdf_parse_binding(b);
    //cout << "finish_load_graph: " << spo.s << " " << spo.p << " " << spo.o << endl;
    triples.push_back(spo);
  }

  const vector<Dict<FreeVar, UOL>>& rows;  
  for (auto& row: rows) {
    if (auto s = row.get(FV("s")); isURI(s)) {
      auto s_uri = asURI(s);
      auto o_uol = row.get(FV("o"));

      RDFNode* n = this->rdf_nodes.get(s_uri);
      if (n == 0) {
	n = this->rdf_nodes.set(s);
	n->node_uri = s;
      }

      auto p_uri = row.get(FV("p"));
      if (p_uri.uri == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type") {
	n->rdfs_classes.insert(asURI(row.get(FV("o"))));
      } else if (p.uri == "http://www.w3.org/ns/shacl#property") {
	auto pp_uri = row.get(FV("pp"));
	n->class_properties.push_back(make_pair(pp_uri, o_uol));
      } else {
	n->triples.push_back(RDFSPO(s_uri, p_uri, o_uol));
      }
    }
  }
#endif
}

shared_ptr<VisNode> RDFNodeManager::create_vis_node(RDFNode* n)
{
    shared_ptr<VisNode> ret;
    if (n->rdfs_classes.contains(URI{"http://www.w3.org/2000/01/rdf-schema#Class"})) {
      auto v_n = make_shared<VisNode_RDFSClass>(n->node_uri);
      ret = v_n;	  
    } else {
      auto v_n = make_shared<VisNode_Data>();
      v_n->uri = n->node_uri.uri;

      for (auto& uri: n->rdfs_classes) {
	v_n->rdfs_classes.push_back(uri.uri);
      }
      for (auto& spo: n->triples) {
	if (spo.p.uri == "gse:node_vis_color") {
	  v_n->node_vis_color = get_display_value(spo.o);
	} else { // if (p.uri == "simple:name") {
	  v_n->members.push_back(DataNodeMember{spo.p.uri, get_display_value(spo.o)});
	}
      }
      
      ret = v_n;
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
  // sparql query to flatten sh:property
  constexpr auto rq_fmt = R"(
  select ?s ?p ?pp ?o where {{
   ?g gse:path "{}"
   graph ?g {{
    {{ 
      ?s ?p ?o filter(!isBlank(?s) && ?p != sh:property)
    }}
    union 
    {{
      ?s ?p ?bo filter(?p = sh:property). ?bo ?pp ?o 
    }}
   }}
  }}
 )";
  
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
  this->build_rdf_nodes(raw_response);

  for (auto& s: this->rdf_nodes.keys()) {
    auto vn = this->create_vis_node(this->rdf_nodes.get(s));
    vis_node_manager->nodes.set(s, vn);
  }
  
  this->in_progress_load_graph_f = false;
  return true;
}

