// -*- c++ -*-
#include "rdf-manager.h"
#include <iostream>

#include <fmt/format.h>
#include <nlohmann/json.hpp>

#include <lib-utils/known-prefixes.h>
#include <lib-utils/rdf-utils.h>
#include <lib-utils/fuseki-utils.h>

using namespace std;

void RDFManager::process_raw_response(const std::string& raw_response)
{
  auto j = nlohmann::json::parse(raw_response);
  for (auto& row_j: j["results"]["bindings"]) {
    auto spo = fuseki::rdf_parse_binding(row_j);
    auto s = spo.s;
    auto p = spo.p;
    auto o = spo.o;
    cout << s << " " << p << " " << o << endl;
    
    if (p == rdf::type) {
      auto s_uri = asURI(s);
      auto o_uri = asURI(o);
      if (o_uri == rdfs::Class) {
	all_user_classes.add(s_uri);
      } else if (o_uri == sh::NodeShape) {
      } else {
	all_user_objects.add(s_uri);
	auto v = all_user_object_types.get(s_uri);
	if (v == 0) {
	  v = all_user_object_types.set(s_uri);
	}
	v->push_back(o_uri);
      }      
    } else {
      auto S = triples.get(s);
      if (S == 0) {
	S = triples.set(s);
      }
      auto P = S->get(p);
      if (P == 0) {
	P = S->set(p);
      }
      P->push_back(o);
    }
  }
}

void RDFManager::do_dump_shacl()
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

void RDFManager::start_load_graph(const string& fuseki_server_url, const string& kgm_path, const string& kgm_shacl_path)
{
  string rq;
  // sparql query to flatten sh:property
  if (kgm_shacl_path.size() > 0) {
    constexpr auto rq_fmt = R"(
  prefix sh: <http://www.w3.org/ns/shacl#>
  prefix kgm: <kgm:>

  select ?s ?p ?o where {{
   ?g kgm:path "{}". ?g_shacl kgm:path "{}".
   {{ graph ?g {{ ?s ?p ?o }} }} 
   union
   {{ graph ?g_shacl {{ ?s ?p ?o }} }}
  }}
  )";  
    rq = fmt::format(rq_fmt, kgm_path, kgm_shacl_path);
  } else {
    constexpr auto rq_fmt = R"(
  prefix sh: <http://www.w3.org/ns/shacl#>
  prefix kgm: <kgm:>

  select ?s ?p ?o where {{
   ?g kgm:path "{}".
   {{ graph ?g {{ ?s ?p ?o }} }} 
   union
   {{ graph ?g_shacl {{ ?s ?p ?o }} }}
  }}
  )";  
    rq = fmt::format(rq_fmt, kgm_path);
  }
  
  cout << "sending rq: " << rq << endl;
  decltype(HTTPPostRequest::request_headers) req_headers;
  req_headers.push_back({"Content-Type", "application/x-www-form-urlencoded"});
  //req_headers.push_back({"Accept", "application/n-triples"}); // this is for construct query output selection
  HTTPPostRequest req{fuseki_server_url, req_headers, toUrlEncodedForm(map<string, string>{{"query", rq}})};
  this->http_request_handler.send_http_request(req);
  this->in_progress_load_graph_f = true;
}

bool RDFManager::finish_load_graph()
{
  string raw_response;
  if (this->http_request_handler.get_response_non_blocking(&raw_response) == false) {
    return false;
  }

  cout << raw_response << endl;
  this->process_raw_response(raw_response);
  this->in_progress_load_graph_f = false;
  return true;
}

