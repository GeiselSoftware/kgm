//#include <imgui_node_editor.h>
#include <imgui_node_editor_internal.h>
#include <misc/cpp/imgui_stdlib.h>

#include "visnode-userclass.h"
#include <iostream>
using namespace std;

VisNode_UserClass::Member::Member()
{
  this->out_pin_id = VisNode::last_node_id++;
}

VisNode_UserClass::Member::Member(const std::string& member_name, const std::string& member_type)
{
  this->out_pin_id = VisNode::last_node_id++;
  this->member_name = member_name;
  this->member_type = member_type;
}

VisNode_UserClass::VisNode_UserClass(const URI& class_uri) : VisNode{get_next_id(), class_uri}
{
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
    ImGui::InputText("##uri", &this->node_uri.uri);
  } else {
    ImGui::SetNextItemWidth(100);
    ImGui::InputText("##uri", &this->node_uri.uri, ImGuiInputTextFlags_ReadOnly);
  }

  ImGui::Text("This is the input");
  ImGui::SameLine();
  if (ImGui::Button(" + ")) {
    this->members.push_back(Member());
  }
  ImGui::BeginDisabled();
  ImGui::SameLine(); ImGui::Button(" - ");
  ImGui::EndDisabled();

  for (size_t i = 0; i < this->members.size(); i++) {
    ImGui::PushID(i);
    auto& member = this->members[i];
    ImGui::Checkbox("##checkbox_", &member.checkbox_value); ImGui::SameLine();
    ImGui::SetNextItemWidth(100.0f); ImGui::InputText("##edit_k_", &member.member_name); ImGui::SameLine();

    if (1) {
      // imgui-demo.cpp IMGUI_DEMO_MARKER Widget/Combo
      //ImGui::SetNextItemWidth(100.0f); ImGui::InputText("##edit_v_", &member.member_type);
      ImGui::SetNextItemWidth(100.0f);
#if 1
      ImGui::InputText("##edit_v_", &member.member_type);
#else
      // member type comboc box - testing
      static ImGuiComboFlags combo_flags = 0;
      if (ImGui::BeginCombo("##member_type_", member.get_member_type_at(member.combo_selected_index))) {
      //if (ImGui::BeginCombo("##member_type_", "HREN")) {
	for (int nn = 0; nn < 3; nn++) {
	  //ImGui::PushID(nn);
	  bool is_selected = member.combo_selected_index == nn;
	  if (ImGui::Selectable(member.get_member_type_at(nn), is_selected)) {
	    member.combo_selected_index = nn;
	  }
	  if (is_selected) {
	    cout << "SELECTED " << nn << endl;
	    ImGui::SetItemDefaultFocus();
	  }
	  //ImGui::PopID();
	}
	ImGui::EndCombo();
      }
#endif
      if (member.is_member_type_dataclass == false) {
	ImGui::SameLine();
	ed::BeginPin(member.out_pin_id, ed::PinKind::Output); ImGui::Text("->>>"); ed::EndPin();
      }
    }
    ImGui::PopID();
  }

  //ed::BeginPin(this->node_bottom_pin, ed::PinKind::Input); ImGui::Text("BOTTOM"); ed::EndPin();

  ImGui::EndGroup();

  auto end_cur_pos = ImGui::GetCursorPos();

  if (1) {
    auto node_w = ImGui::GetItemRectSize().x;

    ImGui::SetCursorPos(ImVec2(end_cur_pos.x + node_w/2, curr_cursor.y));
    ed::BeginPin(this->node_OutputPinId, ed::PinKind::Output); ImGui::Text("^^^"); ed::EndPin();

    
    ImGui::SetCursorPos(ImVec2(curr_cursor.x + node_w, curr_cursor.y));
    ImGui::Checkbox("##is_editable", &this->is_editable);
    
    ImGui::SetCursorPos(ImVec2(end_cur_pos.x + node_w/2, end_cur_pos.y));
    ed::BeginPin(this->node_bottom_pin, ed::PinKind::Input); ImGui::Text("^^^"); ed::EndPin();
    
    ImGui::SetCursorPos(curr_cursor);
  }

  ImGui::PopID();
  ed::EndNode();
}