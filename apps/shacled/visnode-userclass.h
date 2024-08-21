// -*- c++ -*-
#pragma once

#include <vector>
#include <memory>
#include <string>

#include <lib-utils/rdf-utils.h>
#include "visnode.h"
#include "widgets/toggle-lock.h"

class URI;

class VisNode_DataType : public VisNode
{
public:
  explicit VisNode_DataType(const CURIE& curie, VisManager* vis_man);
  CURIE datatype_curie;
  CURIE get_curie() override;
  void make_frame() override;
};

class VisNode_UserClass : public VisNode
{
public:
  struct Member {
    bool checkbox_value = false;
    ax::NodeEditor::PinId out_pin_id;
    std::shared_ptr<VisLink> member_type_link;    
    CURIE member_name_input, member_type_input;

    bool is_minmax_c_input_valid = false;
    std::string minmaxc_input;
    void init_minmaxc_input();
    void parse_minmaxc_input();
    int min_count = -1, max_count = -1;
        
    Member();
  };

  explicit VisNode_UserClass(const CURIE& class_curie, VisManager* vis_man);
  CURIE get_curie() override;

  CURIE class_curie_input;
  std::vector<Member> members;
  
  bool is_editable = true;
  ImGui::ToggleLock toggle_lock;  

  ed::NodeId ID;
  ed::PinId node_InputPinId, node_OutputPinId;
  ed::PinId node_bottom_pin;
    
  void make_frame() override;
};
