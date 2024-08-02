//#include <imgui_node_editor.h>
#include <imgui_node_editor_internal.h>
#include <misc/cpp/imgui_stdlib.h>
#include <lib-utils/image.h>
#include <lib-utils/known-prefixes.h>

#include "vis-manager.h"
#include "visnode-userclass.h"
#include "rdf-manager.h"

#include <iostream>
using namespace std;


VisNode_UserClass::Member::Member()
{
  this->out_pin_id = VisNode::last_node_id++;
}

VisNode_UserClass::VisNode_UserClass(const CURIE& class_curie, VisManager* vis_man) :
  VisNode_Class{get_next_id(), vis_man},
  toggle_lock("img/lock.png", "img/unlock.png")
{
  this->class_curie_input = class_curie;
  this->node_InputPinId = last_node_id++;
  this->node_OutputPinId = last_node_id++;
  this->node_bottom_pin = last_node_id++;
}

void VisNode_UserClass::make_frame()
{
  ed::BeginNode(this->ID);
  ImGui::PushID(this->ID.Get());

  ImGui::BeginGroup();
  ImVec2 curr_cursor = ImGui::GetCursorPos();
  
  ed::BeginPin(this->node_InputPinId, ed::PinKind::Input);
  ImGui::Text(">>>");
  ed::EndPin();
  
  if (this->is_editable) {
    ImGui::SetNextItemWidth(100);
    bool mod = ImGui::InputText("##uri", &this->class_curie_input.curie);
    if (mod) {
#pragma message("implementation needed")
    }
  } else {
    ImGui::SetNextItemWidth(100);
    ImGui::InputText("##uri", &this->class_curie_input.curie,
                     ImGuiInputTextFlags_ReadOnly);
  }

  ImGui::Text("This is the input");
  ImGui::SameLine();
  if (ImGui::Button(" + ")) {
    this->members.push_back(Member());
  }

  {
    auto disabled = find_if(this->members.begin(), this->members.end(), [](const Member& m) -> bool { return m.checkbox_value; }) == this->members.end();
    if (disabled) {
      ImGui::BeginDisabled();
    }
    ImGui::SameLine();
    if (ImGui::Button(" - ")) {      
      this->members.erase(remove_if(this->members.begin(), this->members.end(), [](const Member& m) -> bool { return m.checkbox_value; }), this->members.end());
    }
    if (disabled) {
      ImGui::EndDisabled();
    }
  }

  for (size_t i = 0; i < this->members.size(); i++) {
    ImGui::PushID(i);
    auto &member = this->members[i];

    ImGui::Checkbox("##checkbox_", &member.checkbox_value);
    ImGui::SameLine();

    {
      auto member_name_check = member.member_name_input.is_wellformed();
      bool need_pop_style = false;
      if (!member_name_check) {
	ImGui::PushStyleColor(ImGuiCol_Text, IM_COL32(0,0,255,255));
	ImGui::PushStyleColor(ImGuiCol_FrameBg, IM_COL32(0,255,0,255));
	need_pop_style = true;
      }
      
      ImGui::SetNextItemWidth(100.0f);
      ImGui::InputText("##edit_k_", &member.member_name_input.curie);
      if (need_pop_style) {
	ImGui::PopStyleColor();
	ImGui::PopStyleColor();
      }
    }
    ImGui::SameLine();

    {
      auto member_type_check = vis_man->is_valid_member_type_curie(member.member_type_input);
      bool need_pop_style = false;
      if (!member_type_check) {
	ImGui::PushStyleColor(ImGuiCol_Text, IM_COL32(0,0,255,255));
	ImGui::PushStyleColor(ImGuiCol_FrameBg, IM_COL32(0,255,0,255));
	need_pop_style = true;
      }

      ImGui::SetNextItemWidth(100.0f);
      bool mod = ImGui::InputText("##member_type_", &member.member_type_input.curie);
      if (need_pop_style) {
	ImGui::PopStyleColor();
	ImGui::PopStyleColor();
      }

      if (mod) {
	// check if we need to change member_type to point to another userclass, or to another dataclass or just hold curie
	if (auto uc = vis_man->find_userclass(member.member_type_input)) {
	  member.member_type.shacl_category = Member::member_type_shacl_category_t::shacl_class;
	  member.member_type.vis_class_ptr = uc;
	} else if (auto dc = vis_man->find_dataclass(member.member_type_input)) {
	  member.member_type.shacl_category = Member::member_type_shacl_category_t::shacl_dataclass;
	  member.member_type.vis_class_ptr = dc;
	} else {
	  member.member_type.shacl_category = Member::member_type_shacl_category_t::kgm_member_type;
	  member.member_type.member_type_curie = member.member_type_input;
	}
      }
    }
    
    if (member.member_type.shacl_category == Member::member_type_shacl_category_t::shacl_class) {
      ImGui::SameLine();
      ed::BeginPin(member.out_pin_id, ed::PinKind::Output);
      ImGui::Text("->>>");
      ed::EndPin();
    }
    ImGui::PopID();
  }

  //ed::BeginPin(this->node_bottom_pin, ed::PinKind::Input); ImGui::Text("BOTTOM"); ed::EndPin();

  ImGui::EndGroup();

  auto end_cur_pos = ImGui::GetCursorPos();

  if (1) {
    auto node_w = ImGui::GetItemRectSize().x;

    ImGui::SetCursorPos(ImVec2(end_cur_pos.x + node_w / 2, curr_cursor.y));
    ed::BeginPin(this->node_OutputPinId, ed::PinKind::Output);
    ImGui::Text("^^^");
    ed::EndPin();

    ImGui::SetCursorPos(ImVec2(curr_cursor.x + node_w, curr_cursor.y));
    //ImGui::Checkbox("##is_editable", &this->is_editable);
    toggle_lock("##is_editable", &this->is_editable);

    ImGui::SetCursorPos(ImVec2(end_cur_pos.x + node_w / 2, end_cur_pos.y));
    ed::BeginPin(this->node_bottom_pin, ed::PinKind::Input);
    ImGui::Text("^^^");
    ed::EndPin();

    ImGui::SetCursorPos(curr_cursor);
  }

  ImGui::PopID();
  ed::EndNode();
}
