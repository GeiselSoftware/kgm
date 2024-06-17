// -*- c++ -*-
#pragma once

#include <string>
#include <vector>
#include "node.h"

struct DataNodeMember
{
  std::string name, value;
};

class DataNode : public Node
{
public:
  explicit DataNode();
  std::vector<std::string> rdfs_classes;
  std::string uri;
  std::string node_vis_color;
  std::vector<DataNodeMember> members;
  
  void make_frame() override;
};

