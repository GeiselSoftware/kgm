// -*- c++ -*-
#include "rdf-manager.h"
#include <iostream>
#include <sstream>

#include <fmt/format.h>
#include <nlohmann/json.hpp>

#include <lib-utils/known-prefixes.h>
#include <lib-utils/rdf-utils.h>
#include <lib-utils/fuseki-utils.h>

using namespace std;

RDFManager::RDFManager(const std::string& fuseki_server_url)
{
  this->fuseki_server_url = fuseki_server_url;
}

CURIE RDFManager::collapse_prefix(const URI& uri)
{
  CURIE ret;
  
  for (auto& [prefix, prefix_uri]: prefixes::known_prefixes) {
    auto idx = uri.uri.find(prefix_uri.uri);
    if (idx == 0) {
      ret = CURIE{prefix + ":" + uri.uri.substr(idx + prefix_uri.uri.size())};
      break;
    }
  }
  
  return ret;
}

URI RDFManager::restore_prefix(const CURIE& curie)
{
  auto idx = curie.curie.find(":");
  if (idx == std::string::npos) {
    return URI();
  }  
  auto curie_prefix = curie.curie.substr(0, idx);

  URI res;
  for (auto& [prefix, prefix_uri]: prefixes::known_prefixes) {
    if (curie_prefix == prefix) {
      res = URI{prefix_uri.uri + curie.curie.substr(idx + 1)};
      break;
    }
  }
  
  return res;
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
      auto o_uri = asURI(o);
      if (o_uri == sh::NodeShape) {
	all_userclasses.insert(s);
      } else {
	all_userobjects.insert(s);
      }
    }
  }

  // all_userobjects still have all_userclass, we need to calc all_userobjects MINUS all_userclasses
  set<RDFSubject> new_all_user_objects;
  std::set_difference(all_userobjects.begin(), all_userobjects.end(),
		      all_userclasses.begin(), all_userclasses.end(),
		      std::inserter(new_all_user_objects, new_all_user_objects.begin()),
		      [](auto& a, auto& b) { return less<RDFSubject>()(a, b); });
  all_userobjects = new_all_user_objects;

  cout << "all_userclasses: ";
  for (auto& s: all_userclasses) {
    cout << s << ", ";
  }
  cout << endl;
  cout << "all_userobjects: ";
  for (auto& s: all_userobjects) {
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

void RDFManager::start_load_graph(const string& kgm_path)
{
  // reset
  all_userclasses.clear();
  all_userobjects.clear();
  triples.clear();
  
  string rq = prefixes::make_turtle_prefixes(true);
  constexpr auto rq_fmt = R"(
  select ?s ?p ?o where {{
   ?g kgm:path "{}".
   graph ?g {{ ?s ?p ?o }}
  }}
  )";  
  rq += fmt::format(rq_fmt, kgm_path);  
  
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

void RDFManager::start_save_graph(const string& kgm_path, const vector<RDFSPO>& triples)
{
#pragma message("NB: hacking with fuseki URLs, remove that ASAP")
  auto idx = fuseki_server_url.find("/query");
  auto fuseki_server_update_url = this->fuseki_server_url.substr(0, idx) + "/update";

  ostringstream values;
  for (auto& [s, p, o]: triples) {
    values << "(" << s << " " << p << " " << o << ")\n";
  }

  string rq = prefixes::make_turtle_prefixes(true);
  constexpr auto rq_fmt = R"(
  delete {{
    graph ?g {{
      ?s ?p ?o
    }}
  }}
  insert {{
    graph ?g {{
      ?ns ?np ?no
    }}
  }}
  where {{
    ?g kgm:path "{}"
    graph ?g {{ ?s ?p ?o }}
    values (?ns ?np ?no)
    {{
      {}
    }}
  }}
  )";
  rq += fmt::format(rq_fmt, kgm_path, values.str());
  
  cout << rq << endl;

  decltype(HTTPPostRequest::request_headers) req_headers;
  req_headers.push_back({"Content-Type", "application/x-www-form-urlencoded"});
  //req_headers.push_back({"Accept", "application/n-triples"}); // this is for construct query output selection
  HTTPPostRequest req{fuseki_server_update_url, req_headers, toUrlEncodedForm(map<string, string>{{"update", rq}})};
  this->http_request_handler.send_http_request(req);
  this->in_progress_save_graph_f = true;
}

bool RDFManager::finish_save_graph()
{
  string raw_response;
  if (this->http_request_handler.get_response_non_blocking(&raw_response) == false) {
    return false;
  }

  /*
    <html>
    <head>
    </head>
    <body>
    <h1>Success</h1>
    <p>
    Update succeeded
    </p>
    </body>
    </html>
  */
  
  cout << raw_response << endl; // fuseki update returns html response as above
  this->in_progress_save_graph_f = false;
  return true;
}
