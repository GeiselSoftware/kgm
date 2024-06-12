#pragma once

#ifdef __EMSCRIPTEN__
#include <emscripten.h>
#endif

#define GLFW_INCLUDE_ES3
#include <GLES3/gl3.h>
#include <GLFW/glfw3.h>

#include <imgui.h>
#include <imgui_impl_glfw.h>
#include <imgui_impl_opengl3.h>
class LoopRunner;
class LoopStep
{
private:
  friend class LoopRunner;
  LoopRunner* loop_runner = 0;

public:
  virtual ~LoopStep() {}

  virtual void before_loop_starts() = 0;
  virtual void make_frame() = 0;
};

class LoopRunner
{
public:
  LoopStep* loop_step = 0;
  explicit LoopRunner(LoopStep* loop_step);

  void run();
    
  GLFWwindow* g_window;
  ImVec4 clear_color = ImVec4(0.45f, 0.55f, 0.60f, 1.00f);
  int g_width;
  int g_height;
  
  void on_size_changed();
  void do_loop_step();
};

int init_imgui(LoopRunner*);
int init(LoopRunner*);
void quit();
int init_gl(LoopRunner* lr);
