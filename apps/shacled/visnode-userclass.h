// -*- c++ -*-
#pragma once

#include <vector>
#include <memory>
#include <string>

#include <lib-utils/rdf-utils.h>
#include "visnode.h"
#include "widgets/toggle-lock.h"

class URI;

class VisNode_UserClass : public VisNode
{
public:
  struct Member {
    bool checkbox_value = false;
    ax::NodeEditor::PinId out_pin_id;

    URIVisRep member_name; // sh:property [ sh:path ?member_name ]
    URIVisRep member_type; // sh:property [ sh:class ?member_type -- or -- sh:property [sh:dataclass ?member_type
    enum class member_type_shacl_category_t { unknown, shacl_dataclass, shacl_class };
    member_type_shacl_category_t member_type_shacl_category = member_type_shacl_category_t::unknown;

    Member();
  };

  explicit VisNode_UserClass(const CURIE& class_curie, VisManager* vis_man);

  URIVisRep class_curie;
  std::vector<Member> members;
  
  bool is_editable = true;
  ImGui::ToggleLock toggle_lock;  
  ed::PinId node_InputPinId, node_OutputPinId;
  ed::PinId node_bottom_pin;
    
  void make_frame() override;
};
