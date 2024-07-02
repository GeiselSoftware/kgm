//#include <imgui_node_editor.h>
#include <imgui_node_editor_internal.h>
#include <misc/cpp/imgui_stdlib.h>

#include "vis-node-rdfsclass.h"
#include <lib-utils/fuseki-utils.h>
#include <iostream>
using namespace std;

RDFSClassMember::RDFSClassMember()
{
  this->out_pin_id = VisNode::last_node_id++;
}

RDFSClassMember::RDFSClassMember(const std::string& member_name, const std::string& member_type)
{
  this->out_pin_id = VisNode::last_node_id++;
  this->member_name = member_name;
  this->member_type = member_type;
}

VisNode_RDFSClass::VisNode_RDFSClass(const URI& class_uri) : VisNode{get_next_id()}
{
  this->uri = class_uri.uri;
  this->node_InputPinId = last_node_id++;
  this->node_OutputPinId = last_node_id++;
  this->node_bottom_pin = last_node_id++;
}

void VisNode_RDFSClass::make_frame()
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
    ImGui::InputText("##uri", &this->uri);
  } else {
    ImGui::SetNextItemWidth(100);
    ImGui::InputText("##uri", &this->uri, ImGuiInputTextFlags_ReadOnly);
  }

  ImGui::Text("This is the input");
  ImGui::SameLine();
  if (ImGui::Button(" + ")) {
    this->members.push_back(RDFSClassMember());
  }
  ImGui::BeginDisabled();
  ImGui::SameLine(); ImGui::Button(" - ");
  ImGui::EndDisabled();

  for (size_t i = 0; i < this->members.size(); i++) {
    ImGui::PushID(i);
    auto& member = this->members[i];
    ImGui::Checkbox("##checkbox_", &member.checkbox_value); ImGui::SameLine();
    ImGui::SetNextItemWidth(100.0f); ImGui::InputText("##edit_k_", &member.member_name); ImGui::SameLine();
    ImGui::SetNextItemWidth(100.0f); ImGui::InputText("##edit_v_", &member.member_type); ImGui::SameLine();
    ed::BeginPin(member.out_pin_id, ed::PinKind::Output); ImGui::Text("->>>"); ed::EndPin();
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
