#include "vis-manager.h"
#include <memory>
#include <iostream>
#include <imgui_node_editor.h>
#include <lib-utils/known-prefixes.h>
#include "visnode.h"
#include "rdf-manager.h"
#include "visnode-userclass.h"
#include "visnode-userobject.h"

using namespace std;

void VisManager::build(RDFManager* rdf_man)
{
  for (const RDFSubject& user_class: rdf_man->all_user_classes) {
    auto v_n = make_shared<VisNode_UserClass>(asURI(user_class));
    Dict<RDFPredicate, vector<RDFObject>>* user_class_doubles = rdf_man->triples.get(user_class);
    if (user_class_doubles) {
      vector<RDFObject>* sh_props_oo = user_class_doubles->get(RDFPredicate(sh::property));
      if (sh_props_oo) {
	for (RDFObject& sh_props_o: *sh_props_oo) {
	  Dict<RDFPredicate, vector<RDFObject>>* sh_props_o_doubles = rdf_man->triples.get(RDFSubject(asBNode(sh_props_o)));
	  if (sh_props_o_doubles) { 
	    VisNode_UserClass::Member m;
	    for (auto& [prop_p, prop_v]: *sh_props_o_doubles) {
	      //cout << "prop_v: " << prop_p << " " <<  endl;
	      //cout << "   >>>> display: " << get_display_value(prop_v[0]) << endl;
	      if (asURI(prop_p) == sh::path) {
		assert(prop_v.size() >= 1 && isURI(prop_v[0]));
		m.member_name_rep.update(asURI(prop_v[0]));
	      } else if (asURI(prop_p) == sh::class_) {
		assert(prop_v.size() >= 1 && isURI(prop_v[0]));
		m.is_member_type_dataclass = false;
		m.member_type_rep.update(asURI(prop_v[0]));
	      } else if (asURI(prop_p) == sh::dataclass) {
		assert(prop_v.size() >= 1 && isURI(prop_v[0]));
		m.is_member_type_dataclass = true;
		m.member_type_rep.update(asURI(prop_v[0]));
	      }
	    }
	    v_n->members.push_back(m);
	  }
	}
      }
    }
    this->nodes.set(asURI(user_class), v_n);
  }

  for (const RDFSubject& user_object: rdf_man->all_user_objects) {
    auto v_n = make_shared<VisNode_UserObject>(asURI(user_object));
    for (auto [p, O]: *rdf_man->triples.get(user_object)) {
      for (RDFObject& o: O) {
	v_n->members.push_back(VisNode_UserObject::Member{get_display_value(p), get_display_value(o)});      
      }
    }
    this->nodes.set(asURI(user_object), v_n);
  }
}

void VisManager::make_frame()
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
	  this->links.push_back(make_shared<VisLink>(ed::LinkId(VisNode::get_next_id()), inputPinId, outputPinId));
		  
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
