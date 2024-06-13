// -*- c++ -*-
#pragma once

#include <memory>
#include <imgui_node_editor.h>

namespace ed = ax::NodeEditor;

class Node : public std::enable_shared_from_this<Node>
{
public:
  static int last_node_id;
  static int get_next_id();
  
  ed::NodeId ID;

  explicit Node(int new_node_id);
  std::shared_ptr<Node> get_ptr() { return shared_from_this(); }
  
  virtual ~Node() = 0;
  virtual void make_frame() = 0;
};

struct NodeIdLess
{
    bool operator()(const ed::NodeId& lhs, const ed::NodeId& rhs) const
    {
        return lhs.AsPointer() < rhs.AsPointer();
    }
};

struct Link
{
  ed::LinkId ID;
  
  ed::PinId StartPinID;
  ed::PinId EndPinID;

  ImColor Color;
  
  Link(ed::LinkId id, ed::PinId startPinId, ed::PinId endPinId):
    ID(id), StartPinID(startPinId), EndPinID(endPinId), Color(255, 255, 255)
  {
  }
};
