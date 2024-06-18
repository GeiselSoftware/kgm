#include "node-manager.h"
#include "rdfsclass-node.h"
#include <iostream>

#include <fmt/format.h>
#include <nlohmann/json.hpp>
#include <lib-utils/fuseki-utils.h>
#include "data-node.h"

using namespace std;

void NodeManager::do_dump_shacl()
{
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
}

void NodeManager::start_load_graph(const string& gse_path, const string& fuseki_server_url)
{
  constexpr auto rq_fmt = R"(prefix gse: <gse:> select ?s ?p ?o {{ ?g gse:path "{}" . graph ?g {{ ?s ?p ?o }} }})";
  string rq = fmt::format(rq_fmt, gse_path);
  cout << "sending rq: " << rq << endl;
  HTTPPostRequest req{fuseki_server_url, toUrlEncodedForm(map<string, string>{{"query", rq}})};
  this->http_request_handler.send_http_request(req);
  this->in_progress_load_graph_f = true;
}

bool NodeManager::finish_load_graph()
{
  string raw_response;
  if (this->http_request_handler.get_response_non_blocking(&raw_response) == false) {
    return false;
  }

  cout << raw_response << endl;
  auto j = nlohmann::json::parse(raw_response);
  for (auto& b: j["results"]["bindings"]) {
    auto [s, p, o] = rdf_parse_binding(b);
    cout << "finish_load_graph: " << s << " " << p << " " << o << endl;
    if (p.uri == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type") {
      if (!nodes.has_key(s)) {
	auto new_node = make_shared<DataNode>();
	new_node->uri = s.uri;
	nodes.set(URIRef{new_node->uri}, new_node->get_ptr());	
      }
      auto n = nodes.get<DataNode>(s);
      n->rdfs_classes.push_back(get_display_value(o));
    } else if (p.uri == "gse:node_vis_color") {
      auto n = nodes.get<DataNode>(s);
      n->node_vis_color = get_display_value(o);
    } else { // if (p.uri == "simple:name") {
      auto n = nodes.get<DataNode>(s);
      n->members.push_back(DataNodeMember{p.uri, get_display_value(o)});
    }
  }

  this->in_progress_load_graph_f = false;
  return true;
}

void NodeManager::make_frame()
{
  // show all nodes
  for (auto [_, node]: this->nodes) {
    node->make_frame();
  }

  // show all links
  for (auto link: this->links) {
    ed::Link(link->ID, link->StartPinID, link->EndPinID);
  }

  // Handle creation action, returns true if editor want to create new object (node or link)
  if (ed::BeginCreate()) {
    ed::PinId inputPinId, outputPinId;
    if (ed::QueryNewLink(&inputPinId, &outputPinId)) {
      // QueryNewLink returns true if editor want to create new link between pins.
      //
      // Link can be created only for two valid pins, it is up to you to
      // validate if connection make sense. Editor is happy to make any.
      //
      // Link always goes from input to output. User may choose to drag
      // link from output pin or input pin. This determine which pin ids
      // are valid and which are not:
      //   * input valid, output invalid - user started to drag new ling from input pin
      //   * input invalid, output valid - user started to drag new ling from output pin
      //   * input valid, output valid   - user dragged link over other pin, can be validated
	      
      if (inputPinId && outputPinId) { // both are valid, let's accept link
	// ed::AcceptNewItem() return true when user release mouse button.
	if (ed::AcceptNewItem()) {
	  // Since we accepted new link, lets add one to our list of links.
	  this->links.push_back(make_shared<Link>(ed::LinkId(Node::get_next_id()), inputPinId, outputPinId));
		  
	  // Draw new link.
	  auto back_link = this->links.back();
	  cout << "new link: " << back_link->ID.Get() << " " << back_link->StartPinID.Get() << "->" << back_link->EndPinID.Get() << endl;
	  ed::Link(back_link->ID, back_link->StartPinID, back_link->EndPinID);
	}
		
	// You may choose to reject connection between these nodes
	// by calling ed::RejectNewItem(). This will allow editor to give
	// visual feedback by changing link thickness and color.
      }
    }
  }
  ed::EndCreate(); // Wraps up object creation action handling.

  // Handle deletion action
  if (ed::BeginDelete()) {
    // There may be many links marked for deletion, let's loop over them.
    ed::LinkId deletedLinkId;
    while (ed::QueryDeletedLink(&deletedLinkId)) {
      // If you agree that link can be deleted, accept deletion.
      if (ed::AcceptDeletedItem()) {
	// Then remove link from your data.
	for (auto it = this->links.begin(); it != this->links.end(); ++it) {
	  if ((*it)->ID == deletedLinkId) {
	    this->links.erase(it);
	    break;
	  }
	}
      }

      // You may reject link deletion by calling:
      // ed::RejectDeletedItem();
    }
  }
  ed::EndDelete(); // Wrap up deletion action  
}
