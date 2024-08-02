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

#if 0
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
#endif

void VisManager::add_new_userclass()
{
  static int noname_c = 1;
  auto new_class_curie = CURIE{"noname" + std::to_string(noname_c++)};
  auto v_n = make_shared<VisNode_UserClass>(new_class_curie, this);
  this->nodes.push_back(v_n);
}

void VisManager::build()
{
  // reset
  this->nodes.clear();
  this->links.clear();
  this->shacl_dump.clear();
  
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
		auto o_uri = asURI(prop_v[0]);
		if (o_uri != kgm::placeholder) {
		  m.member_name_input = rdf_man->asCURIE(o_uri);
		}
	      } else if (asURI(prop_p) == kgm::member_name) {
		m.member_name_input.curie = asLiteral(prop_v[0]).literal;
	      } else if (asURI(prop_p) == sh::class_) {
		assert(prop_v.size() >= 1 && isURI(prop_v[0]));
		if (auto curie = rdf_man->asCURIE(asURI(prop_v[0]));
		    auto uc = this->find_userclass(curie)) {
		  m.member_type.shacl_category = VisNode_UserClass::Member::member_type_shacl_category_t::shacl_class;
		  m.member_type.vis_class_ptr = uc;
		  m.member_type_input = uc->class_curie_input;
		} else { // userclass was not found, fallback to kgm_member_type
		  m.member_type.shacl_category = VisNode_UserClass::Member::member_type_shacl_category_t::kgm_member_type;
		  m.member_type.member_type_curie.curie = asLiteral(prop_v[0]).literal;
		  m.member_type_input = m.member_type.member_type_curie;
		}
	      } else if (asURI(prop_p) == sh::dataclass) {
		assert(prop_v.size() >= 1 && isURI(prop_v[0]));
		if (auto curie = rdf_man->asCURIE(asURI(prop_v[0]));
		    auto dc = this->find_dataclass(curie)) {
		  m.member_type.shacl_category = VisNode_UserClass::Member::member_type_shacl_category_t::shacl_dataclass;
		  m.member_type.vis_class_ptr = dc;
		} else { // dataclass was not found, fallback to kgm_member_type
		  m.member_type.shacl_category = VisNode_UserClass::Member::member_type_shacl_category_t::kgm_member_type;
		  m.member_type.member_type_curie.curie = asLiteral(prop_v[0]).literal;
		  m.member_type_input = m.member_type.member_type_curie;
		}
	      } else if (asURI(prop_p) == kgm::member_type) {
		m.member_type.shacl_category = VisNode_UserClass::Member::member_type_shacl_category_t::kgm_member_type;
		m.member_type.member_type_curie.curie = asLiteral(prop_v[0]).literal;
		m.member_type_input = m.member_type.member_type_curie;
	      }
	    }
	    v_n->members.push_back(m);
	  }
	}
      }
    }
    this->nodes.push_back(v_n);
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
    this->nodes.push_back(v_n);
  }

  // second pass over all user classes using only stored information, no access to triples
  // will set up all links
  for (auto n: this->nodes) {
    auto uc = std::dynamic_pointer_cast<VisNode_UserClass>(n);
    if (!uc) {
      continue;
    }
    for (auto& m: uc->members) {
      if (m.member_type.shacl_category == VisNode_UserClass::Member::member_type_shacl_category_t::shacl_class) {
	auto from_uc_node_port_pin_id = m.out_pin_id;
	auto to_uc = dynamic_pointer_cast<VisNode_UserClass>(m.member_type.vis_class_ptr);
	assert(to_uc);
	shared_ptr<VisLink> v_l = make_shared<VisLink>(VisNode::get_next_id(), m.out_pin_id, to_uc->node_InputPinId);
	this->links.push_back(v_l);
      }
    }
  }
}

void VisManager::dump_shacl()
{
  ostringstream out;
  out << prefixes::make_turtle_prefixes(false);
  
  for (auto n: this->nodes) {
    if (auto node = dynamic_pointer_cast<VisNode_UserClass>(n); node) {
      out << node->class_curie_input << " "
	  << rdf_man->asCURIE(rdf::type) << " " << rdf_man->asCURIE(rdfs::Class) << "; ";
      out << rdf_man->asCURIE(rdf::type) << " " << rdf_man->asCURIE(sh::NodeShape) << ";" << endl;
      for (auto& m: node->members) {
	out << "  " << rdf_man->asCURIE(sh::property) << " ["
	    << rdf_man->asCURIE(sh::path) << " " << rdf_man->expand_curie(m.member_name_input) << "; ";
	out << rdf_man->asCURIE(sh::minCount) << " " << "1" << "; "
	    << rdf_man->asCURIE(sh::maxCount) << " " << "1" << "; ";
	switch (m.member_type.shacl_category) {
	case VisNode_UserClass::Member::member_type_shacl_category_t::kgm_member_type:
	  out << kgm::member_type << " " << m.member_type.member_type_curie << "; ";
	  break;
	case VisNode_UserClass::Member::member_type_shacl_category_t::shacl_dataclass:
	  out << rdf_man->asCURIE(sh::dataclass) << " " << rdf_man->expand_curie(m.member_type.vis_class_ptr->get_class_curie());
	  break;
	case VisNode_UserClass::Member::member_type_shacl_category_t::shacl_class:
	  out << rdf_man->asCURIE(sh::class_) << " " << rdf_man->expand_curie(m.member_type.vis_class_ptr->get_class_curie());
	  break;
	}
	out << "];" << endl;
      }
      out << "." << endl << endl;
    }
  }

  this->shacl_dump = out.str();
}

void VisManager::userclasses_to_triples(vector<RDFSPO>* triples)
{
  for (auto n: this->nodes) {
    if (auto node = dynamic_pointer_cast<VisNode_UserClass>(n); node) {
      if (is_wellformed_curie(node->class_curie)) {
	auto node_uri = rdf_man->expand_curie(node->class_curie);
	triples.push_back(RDFSPO(node_uri, rdf::type, rdfs::Class));
	triples.push_back(RDFSPO(node_uri, rdf::type, sh::NodeShape));
      } else {
	auto node_uri = ...;
	triples.push_back(RDFSPO(node_uri, rdf::type, rdfs::Class));
	triples.push_back(RDFSPO(node_uri, rdf::type, sh::NodeShape));
	triples.push_back(RDFSPO(node_uri, kgm::class_curie, Literal(node->class_curie.curie, xsd::string)));
      }
      
      for (auto& m: node->members) {
	BNode bn;
	triples.push_back(RDFSPO(node_uri, sh::property, bn));
	if (this->is_wellformed_curie(m.member_name)) {
	  triples.push_back(RDFSPO(bn, sh::path, rdf_man->expand_curie(m.member_name)));
	} else {
	  triples.push_back(RDFSPO(bn, sh::path, kgm::placeholder));
	  triples.push_back(RDFSPO(bn, kgm::member_name, Literal(m.member_name.curie, xsd::string)));
	}
	triples.push_back(RDFSPO(bn, sh::minCount, Literal(1)));
	triples.push_back(RDFSPO(bn, sh::maxCount, Literal(1)));
	switch (m.member_type_shacl_category) {
	case VisNode_UserClass::Member::member_type_shacl_category_t::unknown:
	  triples.push_back(bn, kgm:member_type, Literal(m.member_type_curie, xsd::string));
	  break;
	case VisNode_UserClass::Member::member_type_shacl_category_t::shacl_dataclass:
	  triples.push_back(RDFSPO(bn, sh::dataclass, m.member_type.sh_dataclass_uri));
	  break;
	case VisNode_UserClass::Member::member_type_shacl_category_t::shacl_class:
	  triples.push_back(RDFSPO(bn, sh::class_, m.member_type.sh_class_ptr->...));
	  break;
	}
      }
    }
  }
}

void VisManager::make_frame()
{
  // show all nodes
  for (auto node: this->nodes) {
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

