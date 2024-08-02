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

#pragma message("asCURIE -- must always succeed???, check all subjs/objs during initial load")
CURIE RDFManager::asCURIE(const URI& uri)
{
  CURIE ret;
  
  bool found = false;
  for (auto& [prefix, prefix_uri]: prefixes::known_prefixes) {
    auto idx = uri.uri.find(prefix_uri.uri);
    if (idx == 0) {
      ret = CURIE{prefix + ":" + uri.uri.substr(idx + prefix_uri.uri.size())};
      found = true;
      break;
    }
  }
  
  if (!found) {
    ret = CURIE{"<" + uri.uri + ">"};
  }
  
  return ret;
}

pair<URI, bool> RDFManager::expand_curie(const CURIE& curie)
{
  URI res;
  auto idx = curie.curie.find(":");
  if (idx == std::string::npos) {
    //throw std::runtime_error(fmt::format("expand_curie failed: {}", curie));
    return make_pair(URI(), false);
  }  
  auto curie_prefix = curie.curie.substr(0, idx);

  bool found = false;
  std::string ret;
  for (auto& [prefix, prefix_uri]: prefixes::known_prefixes) {
    if (curie_prefix == prefix) {
      ret = prefix_uri.uri + curie.curie.substr(idx + 1);
      found = true;
      break;
    }
  }
  
  if (!found) {
    //throw std::runtime_error(fmt::format("can't expand curie {}", curie));
    return make_pair(URI(), false);
  }
  
  return make_pair(URI{ret}, true);
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
      if (o_uri == sh::NodeShape) {
	all_userclasses.insert(s_uri);
      } else {
	all_userobjects.insert(s_uri);
      }
    }
  }

  // all_userobjects still have all_userclass, we need to calc all_userobjects MINUS all_userclasses
  set<URI> new_all_user_objects;
  std::set_difference(all_userobjects.begin(), all_userobjects.end(), all_userclasses.begin(), all_userclasses.end(),
		      std::inserter(new_all_user_objects, new_all_user_objects.begin()),
		      [](auto& a, auto& b) { return a.uri < b.uri; });
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
