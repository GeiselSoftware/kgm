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
  for (auto& row_j: j["results"]["bindings"]) {
    auto spo = fuseki::rdf_parse_binding(row_j);
    //cout << spo.s << " " << spo.p << " " << spo.pp << " " << spo.o << endl;
    assert(isURI(spo.s));
    assert(!isBNode(spo.o));
    auto s_uri = asURI(spo.s);
    auto p_uri = spo.p;
    auto pp_uri = spo.pp;
    auto o_uol = spo.o;
    
    RDFNode* n = this->rdf_nodes.get(s_uri);
    if (n == 0) {
      n = this->rdf_nodes.set(s_uri);
      n->node_uri = s_uri;
    }

    if (p_uri.uri == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type") {
      n->rdfs_classes.insert(asURI(o_uol));
    } else if (pp_uri.uri != "") {
      if (pp_uri.uri == "http://www.w3.org/ns/shacl#dataclass" || pp_uri.uri == "http://www.w3.org/ns/shacl#class") {
	n->class_properties.set(p_uri.uri, get_display_value(spo.o));
      }
    } else {
      n->triples.push_back(RDFSPO{s_uri, p_uri, o_uol});
    }
  }
}

shared_ptr<VisNode> RDFNodeManager::create_vis_node(RDFNode* n)
{
    shared_ptr<VisNode> ret;
    if (n->rdfs_classes.contains(URI{"http://www.w3.org/2000/01/rdf-schema#Class"})) {
      auto v_n = make_shared<VisNode_RDFSClass>(n->node_uri);
      for (auto& cp: n->class_properties) {
	v_n->members.push_back(RDFSClassMember(cp.first, cp.second));
	//cout << cp.first << " " << cp.second << endl;	
      }
      ret = v_n;
    } else {
      auto v_n = make_shared<VisNode_Data>();
      v_n->uri = n->node_uri.uri;

      for (auto& uri: n->rdfs_classes) {
	v_n->rdfs_classes.push_back(uri.uri);
      }
      for (auto& spo: n->triples) {
	if (spo.p.uri == "vgm:node_vis_color") {
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

void RDFNodeManager::start_load_graph(const string& vgm_path, const string& fuseki_server_url)
{
  // sparql query to flatten sh:property
  constexpr auto rq_fmt = R"(
  prefix sh: <http://www.w3.org/ns/shacl#>
  prefix vgm: <vgm:>

  select ?s ?p ?pp ?o where {{
   ?g vgm:path "{}"
   graph ?g {{
    {{ 
      ?s ?p ?o filter(!isBlank(?s) && ?p != sh:property)
    }}
    union 
    {{
      ?s sh:property ?m_props. 
      ?m_props sh:path ?p; ?pp ?o filter (?pp != sh:path)
    }}
   }}
  }}
  )";
  
  string rq = fmt::format(rq_fmt, vgm_path);
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

