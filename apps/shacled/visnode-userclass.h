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
    std::shared_ptr<VisLink> member_type_link;    
    CURIE member_name_input, member_type_input;

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
