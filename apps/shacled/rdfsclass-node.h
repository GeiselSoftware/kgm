// -*- c++ -*-
#pragma once

#include <vector>
#include <memory>
#include <string>

#include "node.h"

struct RDFSClassMember {
  bool checkbox_value = false;
  std::string member_name, member_type;
  ax::NodeEditor::PinId out_pin_id;

  RDFSClassMember();
};

class RDFSClassNode : public Node
{
public:
  explicit RDFSClassNode();
  
  bool is_editable = true;
  
  std::string uri;
  std::string label;
  std::vector<RDFSClassMember> members;
  
  ed::PinId node_InputPinId, node_OutputPinId;
  ed::PinId node_bottom_pin;
  
  
  void make_frame() override;
};

class RDFNode : public Node
{
  void make_frame() override;
};
