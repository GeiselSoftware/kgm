// -*- c++ -*-
#pragma once

#include <memory>
#include <imgui_node_editor.h>
#include <lib-utils/rdf-utils.h>

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
  CURIE from_curie, link_curie, to_curie;
  
  ed::LinkId ID;
  
  ed::PinId StartPinID;
  ed::PinId EndPinID;

  ImColor Color;
  
  explicit VisLink(const CURIE& from_curie, const CURIE& link_curie, const CURIE& to_curie,
		   ed::LinkId id, ed::PinId startPinId, ed::PinId endPinId):
    ID(id), StartPinID(startPinId), EndPinID(endPinId), Color(255, 255, 255)
  {
    this->from_curie = from_curie;
    this->link_curie = link_curie;
    this->to_curie = to_curie;
  }
};
