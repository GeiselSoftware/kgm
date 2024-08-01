#include "visnode-userobject.h"
#include <misc/cpp/imgui_stdlib.h>

VisNode_UserObject::VisNode_UserObject(const CURIE& curie, VisManager* vis_man) :
  VisNode{get_next_id(), vis_man}
{
  this->user_object_curie.set(curie);
}

void VisNode_UserObject::make_frame()
{
  ed::BeginNode(this->ID);
  ImGui::PushID(this->ID.Get());

  ImGui::SetNextItemWidth(100.0f); ImGui::InputText("##uri", &this->user_object_curie.curie.curie, ImGuiInputTextFlags_ReadOnly);

  for (size_t i = 0; i < this->rdfs_classes.size(); i++) {
    ImGui::PushID(i);
    ImGui::SetNextItemWidth(100.0f); ImGui::InputText("##rdfs_class", &rdfs_classes[i].curie);
    if (i < rdfs_classes.size() - 1) {
      ImGui::SameLine();
    }
    ImGui::PopID();
  }
  
  for (size_t i = 0; i < this->members.size(); i++) {
    ImGui::PushID(i);
    auto& member = this->members[i];
    ImGui::SetNextItemWidth(100.0f); ImGui::InputText("##member_name_", &member.name); ImGui::SameLine();
    ImGui::SetNextItemWidth(100.0f); ImGui::InputText("##member_value_", &member.value);
    ImGui::PopID();
  }

  ImGui::SetNextItemWidth(100.0f); ImGui::InputText("##node_vis_color", &this->node_vis_color);
  
  ImGui::PopID();
  ed::EndNode();
}
