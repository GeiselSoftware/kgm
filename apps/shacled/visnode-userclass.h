// -*- c++ -*-
#pragma once

#include <vector>
#include <memory>
#include <string>

#include <lib-utils/rdf-utils.h>
#include "visnode.h"
#include "widgets/toggle-lock.h"

class URI;

class VisNode_Class : public VisNode
{
public:
  explicit VisNode_Class(long unsigned int node_id, VisManager* vis_man) : VisNode(node_id, vis_man) {}
  virtual std::pair<CURIE, URI> get_class_curie() = 0;
};

class VisNode_DataClass : public VisNode_Class
{
public:
  explicit VisNode_DataClass(const CURIE& curie, VisManager* vis_man);
  CURIE dataclass_curie;
  std::pair<CURIE, URI> get_class_curie() override;
  void make_frame() override;
};

class VisNode_UserClass : public VisNode_Class
{
public:
  struct Member {
    bool checkbox_value = false;
    ax::NodeEditor::PinId out_pin_id;

    CURIE member_name_input;
    CURIE member_type_input;
    
    enum class member_type_shacl_category_t { kgm_member_type, shacl_dataclass, shacl_class };    
    struct member_type_t {
      member_type_shacl_category_t shacl_category;
      std::shared_ptr<VisNode_Class> vis_class_ptr;
      CURIE member_type_curie;
    };
    member_type_t member_type;

    Member();
  };

  explicit VisNode_UserClass(const CURIE& class_curie, VisManager* vis_man);
  std::pair<CURIE, URI> get_class_curie() override;

  CURIE class_curie_input;
  std::vector<Member> members;
  
  bool is_editable = true;
  ImGui::ToggleLock toggle_lock;  
  ed::PinId node_InputPinId, node_OutputPinId;
  ed::PinId node_bottom_pin;
    
  void make_frame() override;
};
