// -*- c++ -*-
#pragma once

#include <memory>
#include <imgui_node_editor.h>

namespace ed = ax::NodeEditor;

class VisNode : public std::enable_shared_from_this<VisNode>
{
public:
  static int last_node_id;
  static int get_next_id();
  
  ed::NodeId ID;

  explicit VisNode(int new_node_id);
  std::shared_ptr<VisNode> get_ptr() { return shared_from_this(); }
  
  virtual ~VisNode() = 0;
  virtual void make_frame() = 0;
};

struct VisNodeIdLess
{
    bool operator()(const ed::NodeId& lhs, const ed::NodeId& rhs) const
    {
        return lhs.AsPointer() < rhs.AsPointer();
    }
};

struct VisLink
{
  ed::LinkId ID;
  
  ed::PinId StartPinID;
  ed::PinId EndPinID;

  ImColor Color;
  
  VisLink(ed::LinkId id, ed::PinId startPinId, ed::PinId endPinId):
    ID(id), StartPinID(startPinId), EndPinID(endPinId), Color(255, 255, 255)
  {
  }
};