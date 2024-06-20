// -*- c++ -*-
#pragma once

#include <vector>
#include <memory>

#include <lib-utils/dict.h>
#include <lib-utils/fuseki-utils.h>

class VisNode;
class VisLink;
class VisNodeManager
{
public:  
  Dict<URI, std::shared_ptr<VisNode>> nodes;
  std::vector<std::shared_ptr<VisLink>> links;
  
public:  
  void make_frame();
};

