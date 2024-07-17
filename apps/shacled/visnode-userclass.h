// -*- c++ -*-
#pragma once

#include <vector>
#include <memory>
#include <string>

#include <lib-utils/rdf-utils.h>
#include "visnode.h"


class URI;

class VisNode_UserClass : public VisNode
{
public:
  struct Member {
    bool checkbox_value = false;
    std::string member_name, member_type;
    ax::NodeEditor::PinId out_pin_id;
    
    Member();
    Member(const std::string& member_name, const std::string& member_type);
  };

  explicit VisNode_UserClass(const URI& class_uri);
  
  bool is_editable = true;
  
  std::string label;
  std::vector<Member> members;
  
  ed::PinId node_InputPinId, node_OutputPinId;
  ed::PinId node_bottom_pin;
    
  void make_frame() override;
};
