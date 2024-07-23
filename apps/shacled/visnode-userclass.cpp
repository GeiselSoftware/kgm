//#include <imgui_node_editor.h>
#include <imgui_node_editor_internal.h>
#include <misc/cpp/imgui_stdlib.h>
#include <lib-utils/image.h>

#include "vis-manager.h"
#include "visnode-userclass.h"
#include <iostream>
using namespace std;

VisNode_UserClass::Member::Member() {
  this->out_pin_id = VisNode::last_node_id++;
}

VisNode_UserClass::Member::Member(const URI& member_name_uri, const URI& member_type_uri)
{
  this->member_name_rep = asCURIE(member_name_uri);
  this->member_type_rep = asCURIE(member_type_uri);
  this->out_pin_id = VisNode::last_node_id++;
}

VisNode_UserClass::VisNode_UserClass(const URI& class_uri)
  : VisNode{get_next_id(), class_uri}, toggle_lock("img/lock.png", "img/unlock.png")
{
  this->node_InputPinId = last_node_id++;
  this->node_OutputPinId = last_node_id++;
  this->node_bottom_pin = last_node_id++;
}

void VisNode_UserClass::make_frame() {
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
    ImGui::InputText("##uri", &this->node_uri.uri,
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
    ImGui::SetNextItemWidth(100.0f);
    ImGui::InputText("##edit_k_", &member.member_name_rep);
    ImGui::SameLine();

    ImGui::SetNextItemWidth(100.0f);
#if 0
    // Combo box positioning is broken using imgui-node-editor
    // Use popups instead
    const char* current = member.get_member_type_at(member.combo_selected_index);
    // Open combo box 
    if (ImGui::Button(current)) {
      ed::Suspend();
      ImGui::OpenPopup(("##member_type_" + std::to_string(i)).c_str());
      ed::Resume();
    }
    ed::Suspend();
    if (ImGui::BeginPopup(("##member_type_" + std::to_string(i)).c_str())) {
      for (int nn = 0; nn < 3; nn++) {
        const char* item = member.get_member_type_at(nn);
        if (ImGui::MenuItem(item)) {
          member.combo_selected_index = nn;
          break;
        }
      }
      ImGui::EndPopup();
    }
    ed::Resume();
#else
    ImGui::InputText("##member_type_", &member.member_type_rep);
#endif
    
    if (member.is_member_type_dataclass == false) {
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
