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

  explicit VisNode_UserObject(const CURIE& curie, VisManager*);
  CURIE user_object_curie;
  std::vector<CURIE> rdfs_classes;
  std::string node_vis_color;
  std::vector<Member> members;
  
  void make_frame() override;
};

