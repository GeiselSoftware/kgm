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

  URI dc_uris[] = {xsd::string,xsd::boolean,xsd::decimal,xsd::float_,xsd::double_,xsd::integer,xsd::long_,xsd::int_,xsd::short_,xsd::byte_};
  for (auto& dc_uri: dc_uris) {
    auto dc_curie = rdf_man->collapse_prefix(dc_uri);
    this->visnode_classes_by_curie.set(dc_curie, make_shared<VisNode_DataClass>(dc_curie, this));
  }
}

void VisManager::reset()
{
  this->nodes.clear();
  this->links.clear();
  this->shacl_dump.clear();
}

std::shared_ptr<VisNode_Class> VisManager::find_visnode_class(const CURIE& curie)
{
  return visnode_classes_by_curie.get(curie);
}

void VisManager::add_new_userclass()
{
  static int noname_c = 1;
  auto new_class_curie = CURIE{"noname" + std::to_string(noname_c++)};
  auto v_n = make_shared<VisNode_UserClass>(new_class_curie, this);
  this->nodes.push_back(v_n);

#pragma message("this is a problem: what if CURIE addresses more than one userclass?")
  this->visnode_classes_by_curie.set(new_class_curie, v_n);
}

void VisManager::build_visnode_classes()
{
  // first pass - creating all nodes for user classes
  vector<pair<shared_ptr<VisNode_UserClass>, RDFSubject>> nodes;
  for (const RDFSubject& uc_subj: rdf_man->all_userclasses) {
    CURIE uc_curie;
    if (isBNode(uc_subj)) {
      if (Dict<RDFPredicate, vector<RDFObject>>* user_class_doubles = rdf_man->triples.get(uc_subj)) {
	for (auto& [pred, prop_v]: *user_class_doubles) {
	  if (asURI(pred) == kgm::class_curie) {
	    assert(prop_v.size() == 1 && isLiteral(prop_v[0]));
	    uc_curie = CURIE{asLiteral(prop_v[0]).literal};
	    break;
	  }
	}
      }
    } else if (isURI(uc_subj)) {
      uc_curie = rdf_man->collapse_prefix(asURI(uc_subj));      
    }

    if (uc_curie == CURIE()) {
      ostringstream m; m << "can't convert RDFSubject to CURIE: " << uc_subj;
      throw runtime_error(m.str());
    }

    cout << "VisManager::build, first pass: " << uc_subj << " " << uc_curie << endl;
    auto v_n = make_shared<VisNode_UserClass>(uc_curie, this);
    nodes.push_back(make_pair(v_n, uc_subj));
    this->visnode_classes_by_curie.set(uc_curie, v_n);
  }
  
  // second pass - set up of all user class nodes
  for (auto [n, uc_subj]: nodes) {
    if (auto v_n = dynamic_pointer_cast<VisNode_UserClass>(n)) {
      auto uc_curie = v_n->get_class_curie();
      cout << "VisManager::build, second pass: " << uc_curie << " " << uc_subj << endl;
      if (Dict<RDFPredicate, vector<RDFObject>>* user_class_doubles = rdf_man->triples.get(uc_subj); user_class_doubles == 0) {
	cout << "WARNING: no user_class_doubles found for " << uc_curie << " " << uc_subj << endl;
      } else {
	if (vector<RDFObject>* sh_props_oo = user_class_doubles->get(RDFPredicate(sh::property))) {
	  for (RDFObject& sh_props_o: *sh_props_oo) {
	    if (Dict<RDFPredicate, vector<RDFObject>>* sh_props_o_doubles = rdf_man->triples.get(RDFSubject(asBNode(sh_props_o))); sh_props_o_doubles == 0) {
	      cout << "WARNING: no sh_props_o_doubles found for " << uc_curie << " " << uc_subj << endl;
	    } else {
	      VisNode_UserClass::Member m;
	      for (auto& [prop_p, prop_v]: *sh_props_o_doubles) {
		//cout << "prop_v: " << prop_p << " " <<  endl;
		//cout << "   >>>> display: " << get_display_value(prop_v[0]) << endl;
		if (asURI(prop_p) == sh::path) {
		  assert(prop_v.size() >= 1 && isURI(prop_v[0]));
		  auto o_uri = asURI(prop_v[0]);
		  auto o_curie = rdf_man->collapse_prefix(o_uri);
		  if (o_curie == CURIE()) {
		    throw runtime_error(fmt::format("can't convert URI to CURIE: {}", o_uri.uri));
		  }
		  m.member_name_input = o_curie;
		} else if (asURI(prop_p) == kgm::member_name) {
		  m.member_name_input.curie = asLiteral(prop_v[0]).literal;
		} else if (asURI(prop_p) == sh::class_ || asURI(prop_p) == sh::dataclass) {
		  assert(prop_v.size() >= 1 && isURI(prop_v[0]));
		  auto to_uc_uri = asURI(prop_v[0]);
		  auto to_uc_curie = rdf_man->collapse_prefix(to_uc_uri);
		  if (to_uc_curie == CURIE()) {
		    throw runtime_error(fmt::format("can't collapse prefix for URI {}", to_uc_uri.uri));
		  }
		  m.member_type_input.visnode_class_ptr = this->find_visnode_class(to_uc_curie);
		  if (m.member_type_input.visnode_class_ptr) {
		    assert(m.member_type_input.visnode_class_ptr->get_class_curie() == to_uc_curie);
		    m.member_type_input.curie = to_uc_curie;
		  } else {
		    throw runtime_error(fmt::format("can't find user class with CURIE {}", to_uc_curie.curie));
		  }
		} else if (asURI(prop_p) == kgm::member_type) { // fallback to kgm_member_type
		  assert(prop_v.size() >= 1 && isLiteral(prop_v[0]));
		  auto to_uc_curie = CURIE{asLiteral(prop_v[0]).literal};
		  m.member_type_input.visnode_class_ptr = this->find_visnode_class(to_uc_curie);
		  m.member_type_input.curie = to_uc_curie;
		}
	      }
	      v_n->members.push_back(m);
	    }
	  }
	}
      }
      this->nodes.push_back(v_n);
    }
  }

  // pass over all user classes using only stored information, no access to triples
  // will set up all links
  for (auto n: this->nodes) {
    if (auto uc = std::dynamic_pointer_cast<VisNode_UserClass>(n)) {
      for (auto& m: uc->members) {
	cout << "third pass: " << m.member_name_input << " " << m.member_type_input.curie << endl;
	if (auto to_uc = m.member_type_input.visnode_class_ptr ? dynamic_pointer_cast<VisNode_UserClass>(m.member_type_input.visnode_class_ptr) : 0) {
	  auto from_uc_node_port_pin_id = m.out_pin_id;
	  shared_ptr<VisLink> v_l = make_shared<VisLink>(VisNode::get_next_id(), m.out_pin_id, to_uc->node_InputPinId);
	  this->links.push_back(v_l);
	}
      }
    }
  }
}

void VisManager::build_userobjects()
{
  for (const RDFSubject& uo_subj: rdf_man->all_userobjects) {
    auto user_object = rdf_man->collapse_prefix(asURI(uo_subj));
    auto v_n = make_shared<VisNode_UserObject>(user_object, this);
    for (auto [p, O]: *rdf_man->triples.get(uo_subj)) {
      for (RDFObject& o: O) {
	v_n->members.push_back(VisNode_UserObject::Member{get_display_value(p), get_display_value(o)});
      }
    }
    this->nodes.push_back(v_n);
  }
}

void VisManager::userclasses_to_triples(vector<RDFSPO>* triples)
{
  for (auto n: this->nodes) {
    if (auto uc = dynamic_pointer_cast<VisNode_UserClass>(n); uc) {
      CURIE uc_curie = uc->get_class_curie();
      RDFSubject uc_subj;
      if (auto uc_uri = rdf_man->restore_prefix(uc_curie); uc_uri != URI()) {
	uc_subj = RDFSubject(uc_uri);
	triples->push_back(RDFSPO(uc_subj, rdf::type, rdfs::Class));
	triples->push_back(RDFSPO(uc_subj, rdf::type, sh::NodeShape));
      } else {
	BNode uc_bn;
	uc_subj = RDFSubject(uc_bn);
	triples->push_back(RDFSPO(uc_subj, rdf::type, rdfs::Class));
	triples->push_back(RDFSPO(uc_subj, rdf::type, sh::NodeShape));
	triples->push_back(RDFSPO(uc_subj, kgm::class_curie, Literal(uc_curie.curie, xsd::string)));
      }
      
      for (auto& m: uc->members) {
	BNode bn;
	triples->push_back(RDFSPO(uc_subj, sh::property, bn));
	if (auto path_uri = rdf_man->restore_prefix(m.member_name_input); path_uri != URI()) {
	  triples->push_back(RDFSPO(bn, sh::path, path_uri));
	} else {
#pragma message("do i need kgm::placeholder??")
	  //triples->push_back(RDFSPO(bn, sh::path, kgm::placeholder));
	  triples->push_back(RDFSPO(bn, kgm::member_name, Literal(m.member_name_input.curie, xsd::string)));
	}
	triples->push_back(RDFSPO(bn, sh::minCount, Literal(1)));
	triples->push_back(RDFSPO(bn, sh::maxCount, Literal(1)));
	if (auto visnode_class_ptr = this->find_visnode_class(m.member_type_input.curie)) {
	  auto to_visnode_class_curie = visnode_class_ptr->get_class_curie();
	  assert(to_visnode_class_curie == m.member_type_input.curie);
	  auto to_visnode_class_uri = rdf_man->restore_prefix(to_visnode_class_curie);
	  if (to_visnode_class_uri == URI()) {
	    triples->push_back(RDFSPO(bn, kgm::member_type, Literal(to_visnode_class_curie.curie, xsd::string)));
	  } else {
	    auto pred = dynamic_pointer_cast<VisNode_UserClass>(visnode_class_ptr) ? sh::class_ : sh::dataclass;
	    triples->push_back(RDFSPO(bn, pred, to_visnode_class_uri));
	  }
	} else {
	  triples->push_back(RDFSPO(bn, kgm::member_type, Literal(m.member_type_input.curie.curie, xsd::string)));
	}
      }
    }
  }
}

void VisManager::dump_shacl()
{
#if 0
  vector<RDFSPO> out_triples;
  this->userclasses_to_triples(&out_triples);
  ostringstream out;
  //dump_triples(out, out_triples);
  RDFGraph out_g;
  build_rdf_graph(&out_g, out_triples);
  dump_triples_as_turtle(out, out_g);
  this->shacl_dump = out.str();
#else
  ostringstream out;
  out << prefixes::make_turtle_prefixes(false);

  for (auto n: this->nodes) {
    if (auto node = dynamic_pointer_cast<VisNode_UserClass>(n); node) {
      auto class_curie = node->get_class_curie();

      out << class_curie << " "
	  << rdf_man->collapse_prefix(rdf::type) << " " << rdf_man->collapse_prefix(rdfs::Class) << "; ";
      out << rdf_man->collapse_prefix(rdf::type) << " " << rdf_man->collapse_prefix(sh::NodeShape) << ";" << endl;
      for (auto& m: node->members) {
	out << "  " << rdf_man->collapse_prefix(sh::property) << " ["
	    << rdf_man->collapse_prefix(sh::path) << " "
	    << m.member_name_input.curie << "; ";
	out << rdf_man->collapse_prefix(sh::minCount) << " " << "1" << "; "
	    << rdf_man->collapse_prefix(sh::maxCount) << " " << "1" << "; ";

	if (auto visnode_class_ptr = this->find_visnode_class(m.member_type_input.curie)) {
	  auto pred = dynamic_pointer_cast<VisNode_UserClass>(visnode_class_ptr) ? sh::class_ : sh::dataclass;
	  auto to_visnode_class_curie = visnode_class_ptr->get_class_curie();
	  assert(to_visnode_class_curie == m.member_type_input.curie);
	  out << rdf_man->collapse_prefix(pred) << " " << to_visnode_class_curie << "; ";
	} else {
	  out << rdf_man->collapse_prefix(kgm::member_type) << " " << Literal(m.member_type_input.curie.curie, xsd::string) << "; ";
	}
	out << "];" << endl;
      }
      out << "." << endl << endl;
    }
  }

  this->shacl_dump = out.str();
#endif
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

