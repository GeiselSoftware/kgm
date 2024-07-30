#include "vis-manager.h"
#include <memory>
//#include <iostream>
#include <sstream>
#include <utility>
#include <fmt/format.h>
#include <imgui_node_editor.h>
#include <lib-utils/uuid.h>
#include <lib-utils/known-prefixes.h>
#include "visnode.h"
#include "rdf-manager.h"
#include "visnode-userclass.h"
#include "visnode-userobject.h"

using namespace std;

std::string VisManager::asCURIE(const URI& uri)
{
  bool found = false;
  std::string ret;
  for (auto& [prefix, prefix_uri]: prefixes::known_prefixes) {
    auto idx = uri.uri.find(prefix_uri.uri);
    if (idx == 0) {
      ret = prefix + ":" + uri.uri.substr(idx + prefix_uri.uri.size());
      found = true;
      break;
    }
  }
  
  if (!found) {
    ret = uri.uri;
  }
  
  return ret;
}

URI VisManager::expand_curie(const std::string& curie)
{
  URI res;
  auto idx = curie.find(":");
  if (idx == std::string::npos) {
    //throw std::runtime_error(fmt::format("expand_curie failed: {}", curie));
    return URI{kgm::__prefix_uri.uri + "#error#" + curie};
  }  
  auto curie_prefix = curie.substr(0, idx);

  bool found = false;
  std::string ret;
  for (auto& [prefix, prefix_uri]: prefixes::known_prefixes) {
    if (curie_prefix == prefix) {
      ret = prefix_uri.uri + curie.substr(idx + 1);
      found = true;
      break;
    }
  }
  
  if (!found) {
    //throw std::runtime_error(fmt::format("can't expand curie {}", curie));
    return URI{kgm::__prefix_uri.uri + "#error#" + curie};
  }
  
  return URI{ret};
}

curie_kind VisManager::check_curie(const string& s)
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

    if (!(prefixes::is_prefix(prefix) || prefix == xsd::__prefix)) {
      ret = curie_kind::invalid_curie;
      break;
    }

    if (prefix == xsd::__prefix) {
      ret = curie_kind::valid_curie_dataclass;
      break;
    }

    auto uri = expand_curie(s);
    if (rdf_man->all_user_classes.s.find(uri) != rdf_man->all_user_classes.s.end()) {
      ret = curie_kind::valid_curie_class;
      break;
    }
    
    ret = curie_kind::valid_curie;
  } while(false);
  return ret;
}

VisManager::VisManager(RDFManager* rdf_man)
{
  this->rdf_man = rdf_man;
}

void VisManager::add_new_userclass()
{
  auto new_uri = this->expand_curie("ab:noname-" + generate_uuid_v4());
  auto v_n = make_shared<VisNode_UserClass>(new_uri, this);
  this->nodes.set(new_uri, v_n);  
}

void VisManager::build()
{
  // reset
  this->nodes.clear();
  this->links.clear();
  this->shacl_dump.clear();
  
  Dict<std::pair<URI, URI>, ax::NodeEditor::PinId> member_out_pin_ids;
  
  // first pass - creating all nodes for user classes
  for (const RDFSubject& user_class: rdf_man->all_user_classes) {
    auto v_n = make_shared<VisNode_UserClass>(asURI(user_class), this);
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
		m.member_pred_uri = asURI(prop_v[0]);
		m.member_name_rep = asCURIE(asURI(prop_v[0]));
	      } else if (asURI(prop_p) == sh::class_) {
		assert(prop_v.size() >= 1 && isURI(prop_v[0]));
		m.is_member_type_dataclass = false;
		m.member_type_rep = asCURIE(asURI(prop_v[0]));
	      } else if (asURI(prop_p) == sh::dataclass) {
		assert(prop_v.size() >= 1 && isURI(prop_v[0]));
		m.is_member_type_dataclass = true;
		m.member_type_rep = asCURIE(asURI(prop_v[0]));
	      }
	    }
	    v_n->members.push_back(m);
	    auto out_pin_key = make_pair(asURI(user_class), m.member_pred_uri);
	    member_out_pin_ids.set(out_pin_key, m.out_pin_id);
	  }
	}
      }
    }
    this->nodes.set(asURI(user_class), v_n);
  }

  // first pass for all user objects
  for (const RDFSubject& user_object: rdf_man->all_user_objects) {
    auto v_n = make_shared<VisNode_UserObject>(asURI(user_object), this);
    for (auto [p, O]: *rdf_man->triples.get(user_object)) {
      for (RDFObject& o: O) {
	v_n->members.push_back(VisNode_UserObject::Member{get_display_value(p), get_display_value(o)});      
      }
    }
    this->nodes.set(asURI(user_object), v_n);
  }

  // second pass for all user classes
  for (const RDFSubject& user_class: rdf_man->all_user_classes) {
    Dict<RDFPredicate, vector<RDFObject>>* user_class_doubles = rdf_man->triples.get(user_class);
    if (user_class_doubles) {
      vector<RDFObject>* sh_props_oo = user_class_doubles->get(RDFPredicate(sh::property));
      if (sh_props_oo) {
	for (RDFObject& sh_props_o: *sh_props_oo) {
	  Dict<RDFPredicate, vector<RDFObject>>* sh_props_o_doubles = rdf_man->triples.get(RDFSubject(asBNode(sh_props_o)));
	  if (sh_props_o_doubles) {
	    URI m_pred_uri, to_uc_uri;
	    for (auto& [prop_p, prop_v]: *sh_props_o_doubles) {
	      //cout << "prop_v: " << prop_p << " " <<  endl;
	      //cout << "   >>>> display: " << get_display_value(prop_v[0]) << endl;
	      if (asURI(prop_p) == sh::path) {
		assert(prop_v.size() >= 1 && isURI(prop_v[0]));
		m_pred_uri = asURI(prop_v[0]);
	      } else if (asURI(prop_p) == sh::class_) {
		assert(prop_v.size() >= 1 && isURI(prop_v[0]));
		to_uc_uri = asURI(prop_v[0]);
	      } else if (asURI(prop_p) == sh::dataclass) {
		assert(prop_v.size() >= 1 && isURI(prop_v[0]));
	      }
	    }	  
	  
	    ax::NodeEditor::PinId from_uc_node_port_pin_id = *member_out_pin_ids.get(make_pair(asURI(user_class), m_pred_uri));
	    auto to_uc = dynamic_pointer_cast<VisNode_UserClass>(this->nodes.get(to_uc_uri));	    
	    ax::NodeEditor::PinId to_uc_node_id = to_uc->node_InputPinId;
	    shared_ptr<VisLink> v_l = make_shared<VisLink>(VisNode::get_next_id(), from_uc_node_port_pin_id, to_uc_node_id);
	    this->links.push_back(v_l);
	  }
	}
      }
    }
  }
}

void VisManager::dump_shacl()
{
  ostringstream out;
  out << prefixes::make_turtle_prefixes(false);
  
  for (auto [_, n]: this->nodes) {
    if (auto node = dynamic_pointer_cast<VisNode_UserClass>(n); node) {
      out << node->node_uri << " "
	  << asCURIE(rdf::type) << " " << asCURIE(rdfs::Class) << "; ";
      out << asCURIE(rdf::type) << " " << asCURIE(sh::NodeShape) << ";" << endl;
      for (auto& m: node->members) {
	out << "  " << asCURIE(sh::property) << " ["
	    << asCURIE(sh::path) << " " << expand_curie(m.member_name_rep) << "; ";
	out << asCURIE(sh::minCount) << " " << "1" << "; "
	    << asCURIE(sh::maxCount) << " " << "1" << "; ";
	if (m.is_member_type_dataclass) {
	  out << asCURIE(sh::dataclass) << " " << expand_curie(m.member_type_rep);
	} else {
	  out << asCURIE(sh::class_) << " " << expand_curie(m.member_type_rep);
	}
	out << "];" << endl;
      }
      out << "." << endl << endl;
    }
  }

  this->shacl_dump = out.str();
}

void VisManager::userclasses_to_triples(vector<RDFSPO>* triples_ptr)
{
  auto& triples = *triples_ptr;
  for (auto [_, n]: this->nodes) {
    if (auto node = dynamic_pointer_cast<VisNode_UserClass>(n); node) {
      triples.push_back(RDFSPO(node->node_uri, rdf::type, rdfs::Class));
      triples.push_back(RDFSPO(node->node_uri, rdf::type, sh::NodeShape));
      
      for (auto& m: node->members) {
	BNode bn;
	triples.push_back(RDFSPO(node->node_uri, sh::property, bn));
	triples.push_back(RDFSPO(bn, sh::path, expand_curie(m.member_name_rep)));
	triples.push_back(RDFSPO(bn, sh::minCount, Literal(1)));
	triples.push_back(RDFSPO(bn, sh::maxCount, Literal(1)));
	if (m.is_member_type_dataclass) {
	  triples.push_back(RDFSPO(bn, sh::dataclass, expand_curie(m.member_type_rep)));
	} else {
	  triples.push_back(RDFSPO(bn, sh::class_, expand_curie(m.member_type_rep)));
	}
      }
    }
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

#if 1
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
#endif
}

