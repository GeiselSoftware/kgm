// -*- c++ -*-
#pragma once

#include <memory>
#include <imgui_node_editor.h>
#include <lib-utils/rdf-utils.h>
#include <lib-utils/uuid.h>

namespace ed = ax::NodeEditor;

class VisManager;
class RDFManager;
class VisNode : public std::enable_shared_from_this<VisNode>
{
private:
  static long unsigned int last_node_id;
  
public:
  static long unsigned int get_next_id();

  VisManager* vis_man = 0;
  RDFManager* rdf_man = 0;
  
  explicit VisNode(VisManager*);
  std::shared_ptr<VisNode> get_ptr() { return shared_from_this(); }
  
  virtual ~VisNode() = 0;
  virtual void make_frame() = 0;
  virtual CURIE get_curie() = 0;
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
  std::string uuid;
  ed::LinkId imgui_link_id;  
  ed::PinId StartPinID;
  ed::PinId EndPinID;

  ImColor Color;
  
  explicit VisLink(ed::PinId startPinId, ed::PinId endPinId):
    StartPinID(startPinId), EndPinID(endPinId), Color(255, 255, 255)
  {
    this->uuid = generate_uuid_v4();
    this->imgui_link_id = VisNode::get_next_id();
  }
};
