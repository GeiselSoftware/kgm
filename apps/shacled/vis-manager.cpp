#include "vis-manager.h"
#include <memory>
//#include <iostream>
#include <sstream>
#include <utility>

#ifdef __EMSCRIPTEN__
#include <format>
#define std_format std::format
#else
#include <fmt/format.h>
#define std_format fmt::format
#endif

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
  this->build_visnode_dataclasses();
}

void VisManager::reset()
{
  this->nodes.clear();
  this->links.clear();
  this->shacl_dump.clear();

  this->build_visnode_dataclasses();
}

void VisManager::build_visnode_dataclasses()
{
  URI dc_uris[] = {xsd::string,xsd::boolean,xsd::decimal,xsd::float_,xsd::double_,xsd::integer,xsd::long_,xsd::int_,xsd::short_,xsd::byte_};
  for (auto& dc_uri: dc_uris) {
    auto dc_curie = rdf_man->collapse_prefix(dc_uri);
    cout << "dataclass: " << dc_curie << " " << dc_uri << endl;
    this->nodes.set(dc_curie, make_shared<VisNode_DataType>(dc_curie, this));
  }
}

std::shared_ptr<VisNode> VisManager::find_visnode(const CURIE& curie)
{
  return nodes.get(curie);
}

void VisManager::add_new_userclass()
{
  static int noname_c = 1;
  auto new_class_curie = CURIE{"noname" + std::to_string(noname_c++)};
  auto v_n = make_shared<VisNode_UserClass>(new_class_curie, this);
  this->nodes.set(new_class_curie, v_n);
}

void VisManager::build_visnode_classes()
{
  // first pass - creating all nodes for user classes
  vector<pair<shared_ptr<VisNode_UserClass>, RDFSubject>> nodes_d;
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
    nodes_d.push_back(make_pair(v_n, uc_subj));
    this->nodes.set(uc_curie, v_n);
  }
  
  // second pass - set up of all user class nodes
  for (auto [n, uc_subj]: nodes_d) {
    if (auto v_n = dynamic_pointer_cast<VisNode_UserClass>(n)) {
      auto uc_curie = v_n->get_curie();
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
		    throw runtime_error(std_format("can't convert URI to CURIE: {}", o_uri.uri));
		  }
		  m.member_name_input = o_curie;
		} else if (asURI(prop_p) == kgm::member_name) {
		  m.member_name_input.curie = asLiteral(prop_v[0]).literal;
		} else if (asURI(prop_p) == sh::class_) { // || asURI(prop_p) == sh::dataclass) {
		  assert(prop_v.size() >= 1 && isURI(prop_v[0]));
		  auto to_uc_uri = asURI(prop_v[0]);
		  auto to_uc_curie = rdf_man->collapse_prefix(to_uc_uri);
		  if (to_uc_curie == CURIE()) {
		    throw runtime_error(std_format("can't collapse prefix for URI {}", to_uc_uri.uri));
		  }
		  m.member_type_input = to_uc_curie;
		} else if (asURI(prop_p) == sh::minCount) {
		  assert(prop_v.size() >= 1 && isLiteral(prop_v[0]));
		  m.min_count = asLiteral(prop_v[0]).as_int();
		} else if (asURI(prop_p) == sh::maxCount) {
		  assert(prop_v.size() >= 1 && isLiteral(prop_v[0]));
		  m.max_count = asLiteral(prop_v[0]).as_int();
		} else if (asURI(prop_p) == sh::datatype) {
		  assert(prop_v.size() >= 1 && isURI(prop_v[0]));
		  auto to_dt_uri = asURI(prop_v[0]);
		  auto to_dt_curie = rdf_man->collapse_prefix(to_dt_uri);
		  if (to_dt_curie == CURIE()) {
		    throw runtime_error(std_format("can't collapse prefix for URI {}", to_dt_uri.uri));
		  }
		  m.member_type_input = to_dt_curie;
		} else if (asURI(prop_p) == kgm::member_type) { // fallback to kgm_member_type
		  assert(prop_v.size() >= 1 && isLiteral(prop_v[0]));
		  auto to_uc_curie = CURIE{asLiteral(prop_v[0]).literal};
		  m.member_type_input = to_uc_curie;
		}
	      }
	      
	      if (m.member_name_input.curie == "rdf:type") {
		continue;
	      }
	      m.init_minmaxc_input();
	      v_n->members.push_back(m);
	    }
	  }
	}
      }
      this->nodes.set(uc_curie, v_n);
    }
  }

  // pass over all user classes using only stored information, no access to triples
  // this loop will set up all links
  for (auto& [_, n]: this->nodes) {
    if (auto uc = std::dynamic_pointer_cast<VisNode_UserClass>(n)) {
      cout << "UC: " << uc->get_curie() << endl;
      for (auto& m: uc->members) {
	if (auto to_uc = dynamic_pointer_cast<VisNode_UserClass>(this->find_visnode(m.member_type_input))) {
	  cout << "from: " << m.member_name_input << " " << m.member_type_input
	       << " to: " << to_uc->get_curie()
	       << endl;
	  shared_ptr<VisLink> v_l = make_shared<VisLink>(m.out_pin_id, to_uc->node_InputPinId);
	  m.member_type_link = v_l;
	  this->links.set(v_l->uuid, v_l);
	}
      }
    }
  }
}

void VisManager::build_userobjects()
{
#pragma message("build_userobjects disabled")
  return;
#if 0
  for (const RDFSubject& uo_subj: rdf_man->all_userobjects) {
    auto user_object = rdf_man->collapse_prefix(asURI(uo_subj));
    auto v_n = make_shared<VisNode_UserObject>(user_object, this);
    for (auto [p, O]: *rdf_man->triples.get(uo_subj)) {
      for (RDFObject& o: O) {
	v_n->members.push_back(VisNode_UserObject::Member{get_display_value(p), get_display_value(o)});
      }
    }
    //this->nodes.set(user_object, v_n);
  }
#endif
}

void VisManager::userclasses_to_triples(vector<RDFSPO>* triples)
{
  for (auto& [_, n]: this->nodes) {
    if (auto uc = dynamic_pointer_cast<VisNode_UserClass>(n); uc) {
      CURIE uc_curie = uc->get_curie();
      RDFSubject uc_subj;
      if (auto uc_uri = rdf_man->restore_prefix(uc_curie); uc_uri != URI()) {
	uc_subj = RDFSubject(uc_uri);
	triples->push_back(RDFSPO(uc_subj, rdf::type, rdfs::Class));
	triples->push_back(RDFSPO(uc_subj, rdf::type, sh::NodeShape));
	triples->push_back(RDFSPO(uc_subj, sh::closed, Literal(true)));
      } else {
	BNode uc_bn;
	uc_subj = RDFSubject(uc_bn);
	triples->push_back(RDFSPO(uc_subj, rdf::type, rdfs::Class));
	triples->push_back(RDFSPO(uc_subj, rdf::type, sh::NodeShape));
	triples->push_back(RDFSPO(uc_subj, sh::closed, Literal(true)));
	triples->push_back(RDFSPO(uc_subj, kgm::class_curie, Literal(uc_curie.curie, xsd::string)));
      }

      {
	BNode bn;
	triples->push_back(RDFSPO(uc_subj, sh::property, bn));
	triples->push_back(RDFSPO(bn, sh::path, rdf::type));
	triples->push_back(RDFSPO(bn, sh::class_, rdfs::Class));
	triples->push_back(RDFSPO(bn, sh::minCount, Literal(1)));
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
	
	if (m.min_count >= 0) {
	  triples->push_back(RDFSPO(bn, sh::minCount, Literal(m.min_count)));
	}
	if (m.max_count >= 0) {
	  triples->push_back(RDFSPO(bn, sh::maxCount, Literal(m.max_count)));
	}
	
	if (auto visnode_class_ptr = this->find_visnode(m.member_type_input)) {
	  auto to_visnode_class_curie = m.member_type_input;
	  auto to_visnode_class_uri = rdf_man->restore_prefix(to_visnode_class_curie);
	  if (to_visnode_class_uri == URI()) {
	    triples->push_back(RDFSPO(bn, kgm::member_type, Literal(to_visnode_class_curie.curie, xsd::string)));
	  } else {
	    auto pred = dynamic_pointer_cast<VisNode_UserClass>(visnode_class_ptr) ? sh::class_ : sh::datatype;
	    triples->push_back(RDFSPO(bn, pred, to_visnode_class_uri));
	  }
	} else {
	  triples->push_back(RDFSPO(bn, kgm::member_type, Literal(m.member_type_input.curie, xsd::string)));
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
      auto class_curie = node->get_curie();

      out << class_curie << " "
	  << rdf_man->collapse_prefix(rdf::type) << " " << rdf_man->collapse_prefix(rdfs::Class) << "; ";
      out << rdf_man->collapse_prefix(rdf::type) << " " << rdf_man->collapse_prefix(sh::NodeShape) << "; ";
      out << rdf_man->collapse_prefix(sh::closed) << " " << Literal(true) << "; ";
      out << endl;
      for (auto& m: node->members) {
	out << "  " << rdf_man->collapse_prefix(sh::property) << " ["
	    << rdf_man->collapse_prefix(sh::path) << " "
	    << m.member_name_input.curie << "; ";

	if (m.min_count >= 0) {
	  out << rdf_man->collapse_prefix(sh::minCount) << " " << m.min_count << "; ";
	}
	if (m.max_count >= 0) {
	  out << rdf_man->collapse_prefix(sh::maxCount) << " " << m.max_count << "; ";
	}

	if (auto visnode_class_ptr = this->find_visnode(m.member_type_input)) {
	  auto pred = dynamic_pointer_cast<VisNode_UserClass>(visnode_class_ptr) ? sh::class_ : sh::datatype;
	  auto to_visnode_class_curie = m.member_type_input;
	  out << rdf_man->collapse_prefix(pred) << " " << to_visnode_class_curie << "; ";
	} else {
	  out << rdf_man->collapse_prefix(kgm::member_type) << " " << Literal(m.member_type_input.curie, xsd::string) << "; ";
	}
	out << "];" << endl;
      }
      out << "." << endl << endl;
    }
  }

  this->shacl_dump = out.str();
}

void VisManager::make_frame()
{
  // show all nodes
  for (auto& [_, node]: this->nodes) {
    node->make_frame();
  }

  // show all links
  for (auto& [_, link]: this->links) {
    ed::Link(link->imgui_link_id, link->StartPinID, link->EndPinID);
  }

  if (this->pending_actions.size() > 0) {
    auto action = this->pending_actions.front();
    this->pending_actions.pop_front();
    action->do_it();
    //cout << "pending actions size: " << pending_actions.size() << endl;
  }
  
#if 0
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

