#include "toggle-lock.h"

#include <lib-utils/image.h>

namespace ImGui {

ToggleLock::ToggleLock(const char* lock_path, const char* unlock_path) {
  IM_ASSERT(LoadTextureFromFile(lock_path, &lock_tex, &lock_width, &lock_height));
  IM_ASSERT(LoadTextureFromFile(unlock_path, &unlock_tex, &unlock_width, &unlock_height));
}

// true = unlocked, false = locked
void ToggleLock::operator()(const char* str_id, bool* v) {
  // load correct tex
  ImTextureID tex;
  if (*v) {
    tex = (ImTextureID)lock_tex;
  } else {
    tex = (ImTextureID)unlock_tex;
  }

  ImVec2 p = ImGui::GetCursorScreenPos();

  ImGui::InvisibleButton(str_id, ImVec2(16, 16));
  if (ImGui::IsItemClicked()) *v = !*v;
  ImVec4 tint(1, 1, 1, 1);
  if (ImGui::IsItemHovered()) {
    tint = ImVec4(0.5, 0.5, 0.5, 1);
  }
  ImGui::SetCursorPos(p); 
  ImGui::Image(tex, ImVec2(16, 16), ImVec2(0, 0), ImVec2(1, 1), tint);
}

}