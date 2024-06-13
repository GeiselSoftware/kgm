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
  std::string uri;
  std::vector<DataNodeMember> members;
  
  void make_frame() override;
};

