#include "node-manager.h"
#include "rdfsclass-node.h"
#include <iostream>
using namespace std;

#include <nlohmann/json.hpp>

#include "fuseki-utils.h"

shared_ptr<Node> NodeManager::create_RDFSClassNode()
{
  return make_shared<RDFSClassNode>();
}

void NodeManager::do_dump_shacl()
{
  cout << "SHACL" << endl;
  for (auto n: this->nodes) {
    if (auto node = dynamic_pointer_cast<RDFSClassNode>(n); node) {
      cout << "rdfs class " << node->uri << " " << node->label << endl;
      for (auto& m: node->members) {
	cout << m.member_name << ": " << m.member_type << endl;
      }
    } else {
      cout << "unknown node" << endl;
    }
  }

  for (auto& link: this->links) {
    cout << "link: " << link.ID.Get() << endl;
  }

  cout << "----" << endl;
}

void NodeManager::load_json(const char* rq_result)
{
  auto j = nlohmann::json::parse(rq_result);
  for (auto& b: j["results"]["bindings"]) {
    auto [s, p, o] = rdf_parse_binding(b);
    cout << "load_json: " << s << " " << p << " " << o << endl;
  }
}

void NodeManager::make_frame()
{
  // show all nodes
  for (auto node: this->nodes) {
    node->make_frame();
  }

  // show all links
  for (auto& link: this->links) {
    ed::Link(link.ID, link.StartPinID, link.EndPinID);
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
	  this->links.push_back({ ed::LinkId(Node::get_next_id()), inputPinId, outputPinId });
		  
	  // Draw new link.
	  cout << "new link: " << this->links.back().ID.Get() << " " << this->links.back().StartPinID.Get() << "->" << this->links.back().EndPinID.Get() << endl;
	  ed::Link(this->links.back().ID, this->links.back().StartPinID, this->links.back().EndPinID);
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
	  if ((*it).ID == deletedLinkId) {
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
