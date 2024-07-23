#include <imgui.h>
#include <GL/gl.h>

namespace ImGui {

class ToggleLock {
public:
  ToggleLock(const char* lock_img_path, const char* unlock_img_path);

  void operator()(const char* str_id, bool* v);

private:
  GLuint lock_tex;
  GLuint unlock_tex;

  int lock_width, lock_height, unlock_width, unlock_height;
};

}