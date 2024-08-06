// -*- c++ -*-
#pragma once

#include <vector>
#include <memory>
#include <string>

#include <lib-utils/rdf-utils.h>
#include "visnode.h"
#include "widgets/toggle-lock.h"

class URI;

class VisNode_Class : public VisNode
{
public:
  explicit VisNode_Class(VisManager* vis_man) : VisNode(vis_man) {}
  virtual CURIE get_class_curie() = 0;
};

class VisNode_DataClass : public VisNode_Class
{
public:
  explicit VisNode_DataClass(const CURIE& curie, VisManager* vis_man);
  CURIE dataclass_curie;
  CURIE get_class_curie() override;
  void make_frame() override;
};

class VisNode_UserClass : public VisNode_Class
{
public:
  struct Member {
    bool checkbox_value = false;
    ax::NodeEditor::PinId out_pin_id;

    CURIE member_name_input;
    
    struct member_type_t {
      std::shared_ptr<VisNode_Class> visnode_class_ptr;
      CURIE curie;
    };
    member_type_t member_type_input;

    Member();
  };

  explicit VisNode_UserClass(const CURIE& class_curie, VisManager* vis_man);
  CURIE get_class_curie() override;

  CURIE class_curie_input;
  std::vector<Member> members;
  
  bool is_editable = true;
  ImGui::ToggleLock toggle_lock;  

  ed::NodeId ID;
  ed::PinId node_InputPinId, node_OutputPinId;
  ed::PinId node_bottom_pin;
    
  void make_frame() override;
};

class UserClassNode_delete_class : public Action
{
private:
  CURIE class_curie;
  
public:
  explicit UserClassNode_delete_class(VisManager* vis_man,
				      CURIE class_curie) : Action(vis_man)
  {
    this->class_curie = class_curie;
  }
  
  void do_it() override {
    this->vis_man->nodes.remove(this->class_curie);
  }
};

class UserClassNode_change_class_curie : public Action
{
private:
  std::shared_ptr<VisNode> n;
  CURIE prev_curie;
  
public:
  explicit UserClassNode_change_class_curie(VisManager* vis_man,
					    std::shared_ptr<VisNode> n, CURIE prev_curie) : Action(vis_man)
  {
    this->n = n;
    this->prev_curie = prev_curie;
  }
  
  void do_it() override
  {
    std::shared_ptr<VisNode_UserClass> that = dynamic_pointer_cast<VisNode_UserClass>(this->n);
    
    auto new_curie = that->class_curie_input;
    while (that->vis_man->find_visnode_class(new_curie) != 0) {
      new_curie.curie += "_";
      std::cout << "preventing dup in class curie "
		<< that->class_curie_input
		<< " " << new_curie
		<< std::endl;

    }
    
    this->vis_man->nodes.remove(prev_curie);
    that->class_curie_input = new_curie;
    this->vis_man->nodes.set(new_curie, that);
  }
};
