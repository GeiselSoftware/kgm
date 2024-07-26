// -*- c++ -*-
#pragma once

#include <vector>
#include <memory>
#include <string>

#include <lib-utils/rdf-utils.h>
#include "visnode.h"
#include "widgets/toggle-lock.h"

class URI;

class VisNode_UserClass : public VisNode
{
public:
  struct Member {
    bool checkbox_value = false;
    URI member_pred_uri;
    std::string member_name_rep, member_type_rep;
    bool is_member_type_dataclass = true; // sh:class or sh:dataclass
    ax::NodeEditor::PinId out_pin_id;

    std::vector<std::string> member_types = { "option 1", "option 2", "option 3" };
    const char* get_member_type_at(int idx) { return member_types[idx].c_str(); }
    int combo_selected_index = 1;

    Member();
    Member(const URI& member_name, const URI& member_type);
  };

  explicit VisNode_UserClass(const URI& class_uri);
  
  bool is_editable = true;
  ImGui::ToggleLock toggle_lock;
  
  std::string label;
  std::string class_uri_rep;
  std::vector<Member> members;
  
  ed::PinId node_InputPinId, node_OutputPinId;
  ed::PinId node_bottom_pin;
    
  void make_frame() override;
};
