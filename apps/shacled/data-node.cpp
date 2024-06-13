#include "data-node.h"
#include <misc/cpp/imgui_stdlib.h>

DataNode::DataNode() : Node{get_next_id()}
{
}

void DataNode::make_frame()
{
  ed::BeginNode(this->ID);
  ImGui::PushID(this->ID.Get());

  //ImGui::SetNextItemWidth(100);
  ImGui::InputText("##uri", &this->uri, ImGuiInputTextFlags_ReadOnly);

  ImGui::PopID();
  ed::EndNode();
}
