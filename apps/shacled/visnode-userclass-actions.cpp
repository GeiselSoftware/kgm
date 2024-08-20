#include "visnode-userclass.h"
#include "visnode-userclass-actions.h"

using namespace std;

UserClassNode_delete_class::UserClassNode_delete_class(VisManager* vis_man,
						       CURIE class_curie) : Action(vis_man)
{
  this->class_curie = class_curie;
}

void UserClassNode_delete_class::do_it()
{
  this->vis_man->nodes.remove(this->class_curie);
}

// ................

UserClassNode_change_class_curie::UserClassNode_change_class_curie(VisManager* vis_man,
								   std::shared_ptr<VisNode> userclass_node, CURIE prev_curie) : Action(vis_man)
{
  this->userclass_node = userclass_node;
  this->prev_curie = prev_curie;
}
  
void UserClassNode_change_class_curie::do_it()
{
  std::shared_ptr<VisNode_UserClass> that = dynamic_pointer_cast<VisNode_UserClass>(this->userclass_node);
  auto new_class_curie = that->class_curie_input;
  
  for (auto [_, n]: vis_man->nodes) {
    if (auto uc_n = dynamic_pointer_cast<VisNode_UserClass>(n)) {
      for (auto& m: uc_n->members) {
	if (m.member_type_input == this->prev_curie) {
	  m.member_type_input = new_class_curie;
	}

	if (m.member_type_input == new_class_curie) {
	  if (m.member_type_link) {
	    auto prev_uuid = m.member_type_link->uuid;
	    vis_man->links.remove(prev_uuid);
	  }

	  auto new_link = make_shared<VisLink>(m.out_pin_id, that->node_InputPinId);
	  m.member_type_link = new_link;
	  vis_man->links.set(new_link->uuid, new_link);
	}
      }
    }
  }
  
  this->vis_man->nodes.remove(prev_curie);
  this->vis_man->nodes.set(new_class_curie, that);
}

// .........................

UserClassNode_delete_members::UserClassNode_delete_members(VisManager* vis_man, std::shared_ptr<VisNode> n) :
  Action(vis_man)
{
  this->n = n;
}

void UserClassNode_delete_members::do_it()
{
  auto that = dynamic_pointer_cast<VisNode_UserClass>(this->n);
  for (auto& m: that->members) {
    if (m.checkbox_value == true) {
      if (m.member_type_link) {
	auto mt_uuid = m.member_type_link->uuid;
	vis_man->links.remove(mt_uuid);
	m.member_type_link = 0;
      }
    }
  }
  
  auto res_it = remove_if(that->members.begin(), that->members.end(),
			  [](const VisNode_UserClass::Member& m) -> bool { return m.checkbox_value; });
  that->members.erase(res_it, that->members.end());
}

// .........................

UserClassNode_change_member_type_curie::UserClassNode_change_member_type_curie(VisManager* vis_man,
									       VisNode_UserClass::Member* member_ptr,
									       const CURIE& prev_mtt_curie) :
  Action(vis_man)
{
  this->member_ptr = member_ptr;
  this->prev_member_type_curie = prev_mtt_curie;
}

void UserClassNode_change_member_type_curie::do_it()
{
  if (auto old_to_uc = this->member_ptr->member_type_link) {
    vis_man->links.remove(old_to_uc->uuid);
    this->member_ptr->member_type_link = 0;
  }
  
  if (auto to_uc = dynamic_pointer_cast<VisNode_UserClass>(vis_man->find_visnode(this->member_ptr->member_type_input))) {
    auto new_link = make_shared<VisLink>(member_ptr->out_pin_id, to_uc->node_InputPinId);
    this->member_ptr->member_type_link = new_link;
    vis_man->links.set(new_link->uuid, new_link);
  } else {
    this->member_ptr->member_type_link = 0;
  }
}

