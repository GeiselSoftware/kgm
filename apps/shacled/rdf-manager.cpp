// -*- c++ -*-
#include "rdf-manager.h"
#include <iostream>

#include <fmt/format.h>
#include <nlohmann/json.hpp>

#include <lib-utils/known-prefixes.h>
#include <lib-utils/rdf-utils.h>
#include <lib-utils/fuseki-utils.h>

using namespace std;

RDFManager::RDFManager()
{
  this->known_dataclasses.add(xsd::string);
  this->known_dataclasses.add(xsd::boolean);
  this->known_dataclasses.add(xsd::decimal);
  this->known_dataclasses.add(xsd::float_);
  this->known_dataclasses.add(xsd::double_);
  this->known_dataclasses.add(xsd::integer);
  this->known_dataclasses.add(xsd::long_);
  this->known_dataclasses.add(xsd::int_);
  this->known_dataclasses.add(xsd::short_);
  this->known_dataclasses.add(xsd::byte_);
}
  

void RDFManager::process_raw_response(const std::string& raw_response)
{
  auto j = nlohmann::json::parse(raw_response);
  for (auto& row_j: j["results"]["bindings"]) {
    auto spo = fuseki::rdf_parse_binding(row_j);
    auto s = spo.s;
    auto p = spo.p;
    auto o = spo.o;
    
    if (asURI(p) == rdf::type) {
      auto s_uri = asURI(s);
      auto o_uri = asURI(o);
      if (o_uri == rdfs::Class) {
	all_user_classes.add(s_uri);
      } else if (o_uri == sh::NodeShape) {
	all_user_classes.add(s_uri);
      } else {
	all_user_objects.add(s_uri);
      }
    }
  }

  // all_user_objects still have all_user_class, we need to calc all_user_objects - all_user_classes
  Set<URI> new_all_user_objects;
  std::set_difference(all_user_objects.s.begin(), all_user_objects.s.end(), all_user_classes.s.begin(), all_user_classes.s.end(),
		      std::inserter(new_all_user_objects.s, new_all_user_objects.s.begin()),
		      [](auto& a, auto& b) { return a.uri < b.uri; });
  all_user_objects = new_all_user_objects;

  cout << "all_user_classes: ";
  for (auto& s: all_user_classes) {
    cout << s << ", ";
  }
  cout << endl;
  cout << "all_user_objects: ";
  for (auto& s: all_user_objects) {
    cout << s << ", ";
  }
  cout << endl;

  for (auto& row_j: j["results"]["bindings"]) {
    auto spo = fuseki::rdf_parse_binding(row_j);
    auto s = spo.s;
    auto p = spo.p;
    auto o = spo.o;
    //cout << s << " " << p << " " << o << endl;
    
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

void RDFManager::start_load_graph(const string& fuseki_server_url, const string& kgm_path, const string& kgm_shacl_path)
{
  string rq = make_turtle_prefixes(true);
  // sparql query to flatten sh:property
  if (kgm_shacl_path.size() > 0) {
    constexpr auto rq_fmt = R"(
  select ?s ?p ?o where {{
   ?g kgm:path "{}". 
   ?g_shacl kgm:path "{}".
   {{
     {{ graph ?g {{ ?s ?p ?o }} }} 
     union
     {{ graph ?g_shacl {{ ?s ?p ?o }} }}
   }}
  }}
  )";  
    rq += fmt::format(rq_fmt, kgm_path, kgm_shacl_path);
  } else {
    constexpr auto rq_fmt = R"(
  select ?s ?p ?o where {{
   ?g kgm:path "{}".
   graph ?g {{ ?s ?p ?o }}
  }}
  )";  
    rq += fmt::format(rq_fmt, kgm_path);
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

curie_kind RDFManager::check_curie(const string& s)
{
  curie_kind ret = curie_kind::invalid_curie;
  do {
    int first_colon_idx = s.find(":");
    if (first_colon_idx == string::npos) {
      ret = curie_kind::invalid_curie;
      break;
    }

    string prefix = s.substr(0, first_colon_idx);
    string tail = s.substr(first_colon_idx + 1);

    if (!(is_known_prefix(prefix) || prefix == xsd::__prefix)) {
      ret = curie_kind::invalid_curie;
      break;
    }

    if (prefix == xsd::__prefix) {
      ret = curie_kind::valid_curie_dataclass;
      break;
    }

    auto uri = expand_curie(s);
    if (this->all_user_classes.s.find(uri) != this->all_user_classes.s.end()) {
      ret = curie_kind::valid_curie_class;
      break;
    }
    
    ret = curie_kind::valid_curie;
  } while(false);
  return ret;
}
