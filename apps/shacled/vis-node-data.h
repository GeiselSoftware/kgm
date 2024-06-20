// -*- c++ -*-
#pragma once

#include <string>
#include <vector>
#include "vis-node.h"

struct DataNodeMember
{
  std::string name, value;
};

class VisNode_Data : public VisNode
{
public:
  explicit VisNode_Data();
  std::vector<std::string> rdfs_classes;
  std::string uri;
  std::string node_vis_color;
  std::vector<DataNodeMember> members;
  
  void make_frame() override;
};

