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

VisManager::VisManager(RDFManager* rdf_man)
{
  this->rdf_man = rdf_man;
}

VisManager::curie_kind VisManager::classify_curie(const CURIE& curie)
{
  auto& s = curie.curie;
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

    auto uri = rdf_man->expand_curie(curie);
    if (rdf_man->all_user_classes.s.find(uri) != rdf_man->all_user_classes.s.end()) {
      ret = curie_kind::valid_curie_class;
      break;
    }
    
    ret = curie_kind::valid_curie;
  } while(false);
  return ret;
}


void VisManager::add_new_userclass()
{
  auto new_class_curie = CURIE{"ab:noname-" + generate_uuid_v4()};
  auto v_n = make_shared<VisNode_UserClass>(new_class_curie, this);
  this->nodes.set(new_class_curie, v_n);  
}

void VisManager::build()
{
  // reset
  this->nodes.clear();
  this->links.clear();
  this->shacl_dump.clear();
  
  Dict<std::pair<CURIE, CURIE>, ax::NodeEditor::PinId> member_out_pin_ids;
  
  // first pass - creating all nodes for user classes
  for (const RDFSubject& uc: rdf_man->all_user_classes) {
    auto user_class = rdf_man->asCURIE(asURI(uc));
    auto v_n = make_shared<VisNode_UserClass>(user_class, this);
    Dict<RDFPredicate, vector<RDFObject>>* user_class_doubles = rdf_man->triples.get(uc);
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
		m.member_name.set(rdf_man->asCURIE(asURI(prop_v[0])));
	      } else if (asURI(prop_p) == sh::class_) {
		assert(prop_v.size() >= 1 && isURI(prop_v[0]));
		m.member_type.set(rdf_man->asCURIE(asURI(prop_v[0])));
		m.member_type_shacl_category = VisNode_UserClass::Member::member_type_shacl_category_t::shacl_class;
	      } else if (asURI(prop_p) == sh::dataclass) {
		assert(prop_v.size() >= 1 && isURI(prop_v[0]));
		m.member_type.set(rdf_man->asCURIE(asURI(prop_v[0])));
		m.member_type_shacl_category = VisNode_UserClass::Member::member_type_shacl_category_t::shacl_dataclass;
	      }
	    }
	    v_n->members.push_back(m);
	    auto out_pin_key = make_pair(user_class, m.member_name.curie);
	    member_out_pin_ids.set(out_pin_key, m.out_pin_id);
	  }
	}
      }
    }
    this->nodes.set(user_class, v_n);
  }

  // first pass for all user objects
  for (const RDFSubject& uo: rdf_man->all_user_objects) {
    auto user_object = rdf_man->asCURIE(asURI(uo));
    auto v_n = make_shared<VisNode_UserObject>(user_object, this);
    for (auto [p, O]: *rdf_man->triples.get(uo)) {
      for (RDFObject& o: O) {
	v_n->members.push_back(VisNode_UserObject::Member{get_display_value(p), get_display_value(o)});
      }
    }
    this->nodes.set(user_object, v_n);
  }

  // second pass for all user classes
  for (const RDFSubject& uc: rdf_man->all_user_classes) {
    auto user_class = rdf_man->asCURIE(asURI(uc));
    Dict<RDFPredicate, vector<RDFObject>>* user_class_doubles = rdf_man->triples.get(uc);
    if (user_class_doubles) {
      vector<RDFObject>* sh_props_oo = user_class_doubles->get(RDFPredicate(sh::property));
      if (sh_props_oo) {
	for (RDFObject& sh_props_o: *sh_props_oo) {
	  Dict<RDFPredicate, vector<RDFObject>>* sh_props_o_doubles = rdf_man->triples.get(RDFSubject(asBNode(sh_props_o)));
	  if (sh_props_o_doubles) {
	    CURIE m_name_curie, to_uc_curie;
	    for (auto& [prop_p, prop_v]: *sh_props_o_doubles) {
	      //cout << "prop_v: " << prop_p << " " <<  endl;
	      //cout << "   >>>> display: " << get_display_value(prop_v[0]) << endl;
	      if (asURI(prop_p) == sh::path) {
		assert(prop_v.size() >= 1 && isURI(prop_v[0]));
		m_name_curie = rdf_man->asCURIE(asURI(prop_v[0]));
	      } else if (asURI(prop_p) == sh::class_) {
		assert(prop_v.size() >= 1 && isURI(prop_v[0]));
		to_uc_curie = rdf_man->asCURIE(asURI(prop_v[0]));
	      } else if (asURI(prop_p) == sh::dataclass) {
		assert(prop_v.size() >= 1 && isURI(prop_v[0]));
	      }
	    }	  
	  
	    ax::NodeEditor::PinId from_uc_node_port_pin_id = *member_out_pin_ids.get(make_pair(user_class, m_name_curie));
	    auto to_uc = dynamic_pointer_cast<VisNode_UserClass>(this->nodes.get(to_uc_curie));
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
      out << node->class_curie.curie << " "
	  << rdf_man->asCURIE(rdf::type) << " " << rdf_man->asCURIE(rdfs::Class) << "; ";
      out << rdf_man->asCURIE(rdf::type) << " " << rdf_man->asCURIE(sh::NodeShape) << ";" << endl;
      for (auto& m: node->members) {
	out << "  " << rdf_man->asCURIE(sh::property) << " ["
	    << rdf_man->asCURIE(sh::path) << " " << rdf_man->expand_curie(m.member_name.curie) << "; ";
	out << rdf_man->asCURIE(sh::minCount) << " " << "1" << "; "
	    << rdf_man->asCURIE(sh::maxCount) << " " << "1" << "; ";
	switch (m.member_type_shacl_category) {
	case VisNode_UserClass::Member::member_type_shacl_category_t::unknown:
	  throw runtime_error("unexpected case statement");
	  break;
	case VisNode_UserClass::Member::member_type_shacl_category_t::shacl_dataclass:
	  out << rdf_man->asCURIE(sh::dataclass) << " " << rdf_man->expand_curie(m.member_type.curie);
	  break;
	case VisNode_UserClass::Member::member_type_shacl_category_t::shacl_class:
	  out << rdf_man->asCURIE(sh::class_) << " " << rdf_man->expand_curie(m.member_type.curie);
	  break;
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
      auto node_uri = rdf_man->expand_curie(node->class_curie.curie);
      triples.push_back(RDFSPO(node_uri, rdf::type, rdfs::Class));
      triples.push_back(RDFSPO(node_uri, rdf::type, sh::NodeShape));
      
      for (auto& m: node->members) {
	BNode bn;
	triples.push_back(RDFSPO(node_uri, sh::property, bn));
	triples.push_back(RDFSPO(bn, sh::path, rdf_man->expand_curie(m.member_name.curie)));
	triples.push_back(RDFSPO(bn, sh::minCount, Literal(1)));
	triples.push_back(RDFSPO(bn, sh::maxCount, Literal(1)));
	switch (m.member_type_shacl_category) {
	case VisNode_UserClass::Member::member_type_shacl_category_t::unknown:
	  throw runtime_error("unexpected case statement");
	  break;
	case VisNode_UserClass::Member::member_type_shacl_category_t::shacl_dataclass:
	  triples.push_back(RDFSPO(bn, sh::dataclass, rdf_man->expand_curie(m.member_type.curie)));
	  break;
	case VisNode_UserClass::Member::member_type_shacl_category_t::shacl_class:
	  triples.push_back(RDFSPO(bn, sh::class_, rdf_man->expand_curie(m.member_type.curie)));
	  break;
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

