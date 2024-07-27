// -*- c++ -*-
#pragma once

#include <string>
#include <vector>
#include <lib-utils/rdf-utils.h>
#include "visnode.h"

class VisNode_UserObject : public VisNode
{
public:
  struct Member
  {
    std::string name, value;
  };

  explicit VisNode_UserObject(const URI& uri, RDFManager*);
  std::vector<std::string> rdfs_classes;
  std::string node_vis_color;
  std::vector<Member> members;
  
  void make_frame() override;
};

