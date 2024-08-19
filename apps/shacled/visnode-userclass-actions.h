// -*- c++ -*-
#pragma once

#include "vis-manager.h"

//class UserClassNode_add_class;
class UserClassNode_delete_class;
class UserClassNode_change_class_curie;
//class UserClassNode_add_member;
class UserClassNode_delete_members;
class UserClassNode_change_member_type_curie;

class UserClassNode_delete_class : public Action
{
private:
  CURIE class_curie;
  
public:
  explicit UserClassNode_delete_class(VisManager* vis_man, CURIE class_curie);
  void do_it() override;
};

class UserClassNode_change_class_curie : public Action
{
private:
  std::shared_ptr<VisNode> userclass_node;
  CURIE prev_curie;
  
public:
  explicit UserClassNode_change_class_curie(VisManager* vis_man, std::shared_ptr<VisNode> userclass_node, CURIE prev_curie);
  void do_it() override;
};

class UserClassNode_delete_members : public Action
{
public:
  explicit UserClassNode_delete_members(VisManager* vis_man, std::shared_ptr<VisNode> n);
  void do_it() override;

private:
  std::shared_ptr<VisNode> n;
};

class UserClassNode_change_member_type_curie : public Action
{
public:
  explicit UserClassNode_change_member_type_curie(VisManager* vis_man, VisNode_UserClass::Member* member_ptr, const CURIE& prev_member_type_curie);
  void do_it() override;

private:
  VisNode_UserClass::Member* member_ptr = nullptr;
  CURIE prev_member_type_curie;
};
