//#include <imgui_node_editor.h>
#include <imgui_node_editor_internal.h>
#include <misc/cpp/imgui_stdlib.h>
#include <lib-utils/image.h>
#include <lib-utils/known-prefixes.h>

#include "vis-manager.h"
#include "visnode-userclass.h"
#include "visnode-userclass-actions.h"
#include "rdf-manager.h"

#include <iostream>
using namespace std;

VisNode_DataType::VisNode_DataType(const CURIE& curie, VisManager* vis_man) :
  VisNode(vis_man)
{
  this->datatype_curie = curie;
}

CURIE VisNode_DataType::get_curie()
{
  return this->datatype_curie;
}

void VisNode_DataType::make_frame()
{
}


VisNode_UserClass::Member::Member()
{
  this->out_pin_id = VisNode::get_next_id();
}

VisNode_UserClass::VisNode_UserClass(const CURIE& class_curie, VisManager* vis_man) :
  VisNode(vis_man),
  toggle_lock("img/lock.png", "img/unlock.png")
{
  this->class_curie_input = class_curie;

  this->ID = VisNode::get_next_id();
  this->node_InputPinId = VisNode::get_next_id();
  this->node_OutputPinId = VisNode::get_next_id();
  this->node_bottom_pin = VisNode::get_next_id();
}

CURIE VisNode_UserClass::get_curie()
{
  return this->class_curie_input;
}

static int class_curie_edit_cb(ImGuiInputTextCallbackData* data)
{
  VisNode_UserClass* that = (VisNode_UserClass*)data->UserData;
  //cout << "class_curie_edit_cb: " << data->Buf << endl;
  if (that->vis_man->find_visnode(CURIE{std::string(data->Buf)}) != 0) {
    cout << "preventing dup in class curie " << that->class_curie_input << endl;
    data->InsertChars(0, "_");
  }
  return 0;
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

  {
    bool need_pop_style = false;
    if (!this->class_curie_input.is_good_userclass_curie()) {
      ImGui::PushStyleColor(ImGuiCol_Text, IM_COL32(0,0,255,255));
      ImGui::PushStyleColor(ImGuiCol_FrameBg, IM_COL32(0,255,0,255));
      need_pop_style = true;      
    }
  
    if (this->is_editable) {
      ImGui::SetNextItemWidth(200);
      CURIE prev_curie = this->class_curie_input;
      //if (ImGui::InputText("##uri", &this->class_curie_input.curie)) {
      if (ImGui::InputText("##uri", &this->class_curie_input.curie, ImGuiInputTextFlags_CallbackEdit, class_curie_edit_cb, this)) {
	auto action = make_shared<UserClassNode_change_class_curie>(this->vis_man, this->get_ptr(), prev_curie);
	this->vis_man->pending_actions.push_back(action);	
      }
    } else {
      ImGui::SetNextItemWidth(200);
      ImGui::InputText("##uri", &this->class_curie_input.curie, ImGuiInputTextFlags_ReadOnly);
    }
    if (need_pop_style) {
      ImGui::PopStyleColor();
      ImGui::PopStyleColor();
    }    
  }

  if (ImGui::Button("X")) {
    auto action = make_shared<UserClassNode_delete_class>(this->vis_man, this->class_curie_input);
    this->vis_man->pending_actions.push_back(action);
  }
  
  ImGui::SameLine();
#pragma message("we need action at this point, not good for make_frame")
  if (ImGui::Button(" + ")) {
    auto m = Member();
    m.min_count = m.max_count = 1;    
    this->members.push_back(m);
  }

  {
    auto disabled = find_if(this->members.begin(), this->members.end(), [](const Member& m) -> bool { return m.checkbox_value; }) == this->members.end();
    if (disabled) {
      ImGui::BeginDisabled();
    }
    ImGui::SameLine();
    if (ImGui::Button(" - ")) {
      auto action = make_shared<UserClassNode_delete_members>(this->vis_man, this->get_ptr());
      this->vis_man->pending_actions.push_back(action);
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
      auto member_name_check = member.member_name_input.is_good_predicate();
      bool need_pop_style = false;
      if (!member_name_check) {
	ImGui::PushStyleColor(ImGuiCol_Text, IM_COL32(0,0,255,255));
	ImGui::PushStyleColor(ImGuiCol_FrameBg, IM_COL32(0,255,0,255));
	need_pop_style = true;
      }
      
      ImGui::SetNextItemWidth(150.0f);
      ImGui::InputText("##edit_k_", &member.member_name_input.curie);
      
      if (need_pop_style) {
	ImGui::PopStyleColor();
	ImGui::PopStyleColor();
      }
    }
    ImGui::SameLine();

    {
      auto missing_uri_check = rdf_man->restore_prefix(member.member_type_input) == URI(); // true if no URI for this curie      
      auto missing_curie_type_check = vis_man->find_visnode(member.member_type_input) == 0; // true if curie has no corresponding type node
      
      bool need_pop_style = false;
      if (missing_uri_check || missing_curie_type_check) {
	ImGui::PushStyleColor(ImGuiCol_Text, IM_COL32(0,0,255,255));
	ImGui::PushStyleColor(ImGuiCol_FrameBg, IM_COL32(0,255,0,255));
	need_pop_style = true;
      }

      ImGui::SetNextItemWidth(150.0f);
      CURIE prev_member_type_curie = member.member_type_input;
      if (ImGui::InputText("##member_type_", &member.member_type_input.curie)) {
	auto action = make_shared<UserClassNode_change_member_type_curie>(this->vis_man, &member, prev_member_type_curie);
	this->vis_man->pending_actions.push_back(action);
      }

      if (need_pop_style) {
	ImGui::PopStyleColor();
	ImGui::PopStyleColor();
      }
    }
    
    if (dynamic_pointer_cast<VisNode_UserClass>(vis_man->find_visnode(member.member_type_input))) {
      ImGui::SameLine();
      ed::BeginPin(member.out_pin_id, ed::PinKind::Output);
      ImGui::Text("->>>");
      ed::EndPin();
    }
    ImGui::PopID();
  }

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
