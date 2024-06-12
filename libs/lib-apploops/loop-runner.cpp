#include "loop-runner.h"
#include <functional>
#include <iostream>
using namespace std;

#ifdef __EMSCRIPTEN__
#include <emscripten.h>

// Function used by c++ to get the size of the html canvas
EM_JS(int, canvas_get_width, (), {
    return Module.canvas.width;
  });
  
// Function used by c++ to get the size of the html canvas
EM_JS(int, canvas_get_height, (), {
    return Module.canvas.height;
  });
  
// Function called by javascript
EM_JS(void, resizeCanvas, (), {
    js_resizeCanvas();
  });
#endif

void desktop_run_main_loop(LoopRunner* lr)
{
  while (!glfwWindowShouldClose(lr->g_window)) {
    lr->do_loop_step();
  }
  cout << "imgui loop exited" << endl;
  
  // Cleanup
  ImGui_ImplOpenGL3_Shutdown();
  ImGui_ImplGlfw_Shutdown();
  ImGui::DestroyContext();
  
  glfwDestroyWindow(lr->g_window);
  cout << "desktop_run_main_loop exited" << endl;
}


static LoopRunner* that = 0;
void cbf() { that->do_loop_step(); }

LoopRunner::LoopRunner(LoopStep* loop_step)
{
  that = this;
  this->loop_step = loop_step;
  this->loop_step->loop_runner = this;
  
#ifdef __EMSCRIPTEN__
  g_width = canvas_get_width();
  g_height = canvas_get_height();
#else
  // NB: desktop run sizes
  g_width = 1440;
  g_height = 800;
#endif

}


void LoopRunner::run()
{
#ifdef __EMSCRIPTEN__
  emscripten_set_main_loop(cbf, 0, 1);
#else
  desktop_run_main_loop(this);
#endif
}

void LoopRunner::on_size_changed()
{
  glfwSetWindowSize(g_window, g_width, g_height);
  ImGui::SetCurrentContext(ImGui::GetCurrentContext());
}

void LoopRunner::do_loop_step()
{
#ifdef __EMSCRIPTEN__
  int width = canvas_get_width();
  int height = canvas_get_height();
    
  if (width != g_width || height != g_height)
    {
      g_width = width;
      g_height = height;
      on_size_changed();
    }
#endif

  glfwPollEvents();

  ImGui_ImplOpenGL3_NewFrame();
  ImGui_ImplGlfw_NewFrame();
  ImGui::NewFrame();

  loop_step->make_frame();
    
  ImGui::Render();

  int display_w, display_h;
  glfwMakeContextCurrent(g_window);
  glfwGetFramebufferSize(g_window, &display_w, &display_h);
  glViewport(0, 0, display_w, display_h);
  glClearColor(clear_color.x, clear_color.y, clear_color.z, clear_color.w);
  glClear(GL_COLOR_BUFFER_BIT);

  ImGui_ImplOpenGL3_RenderDrawData(ImGui::GetDrawData());

#ifdef __EMSCRIPTEN__
  glfwMakeContextCurrent(g_window);
#else
  glfwSwapBuffers(g_window);
#endif

}


// ..............................

int init_imgui(LoopRunner* lr)
{
  // Setup Dear ImGui binding
  IMGUI_CHECKVERSION();
  ImGui::CreateContext();

  ImGuiIO& io = ImGui::GetIO(); (void)io;

  // Enable Docking
  //io.ConfigFlags |= ImGuiConfigFlags_DockingEnable;
  
  ImGui_ImplGlfw_InitForOpenGL(lr->g_window, true);
  ImGui_ImplOpenGL3_Init();

  // Setup style
  ImGui::StyleColorsDark();

  io.Fonts->AddFontFromFileTTF("fonts/xkcd-script.ttf", 23.0f);
  io.Fonts->AddFontFromFileTTF("fonts/xkcd-script.ttf", 18.0f);
  io.Fonts->AddFontFromFileTTF("fonts/xkcd-script.ttf", 26.0f);
  io.Fonts->AddFontFromFileTTF("fonts/xkcd-script.ttf", 32.0f);
  io.Fonts->AddFontDefault();

  lr->loop_step->before_loop_starts();
  
#ifdef __EMSCRIPTEN__
  resizeCanvas();
#endif

  return 0;
}


int init(LoopRunner* lr)
{
  init_gl(lr);
  init_imgui(lr);
  return 0;
}


void quit()
{
  glfwTerminate();
}

int init_gl(LoopRunner* lr)
{
  if( !glfwInit() )
  {
    cout << "Failed to initialize GLFW" << endl;
      return 1;
  }

#ifdef __EMSCRIPTEN__
  glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE); // We don't want the old OpenGL
#else
  #if defined(IMGUI_IMPL_OPENGL_ES2)
    // GL ES 2.0 + GLSL 100
    const char* glsl_version = "#version 100";
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 2);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 0);
    glfwWindowHint(GLFW_CLIENT_API, GLFW_OPENGL_ES_API);
  #elif defined(__APPLE__)
    // GL 3.2 + GLSL 150
    const char* glsl_version = "#version 150";
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 2);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);  // 3.2+ only
    glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE);            // Required on Mac
  #else
    // GL 3.0 + GLSL 130
    const char* glsl_version = "#version 130";
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 0);
    //glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);  // 3.2+ only
    //glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE);            // 3.0+ only
  #endif
#endif

  // Open a window and create its OpenGL context
  int canvasWidth = lr->g_width;
  int canvasHeight = lr->g_height;
  lr->g_window = glfwCreateWindow(canvasWidth, canvasHeight, "WebGui Demo", NULL, NULL);
  if( lr->g_window == NULL )
  {
    cout << "Failed to open GLFW window." << endl;
      glfwTerminate();
      return -1;
  }
  glfwMakeContextCurrent(lr->g_window); // Initialize GLEW

  return 0;
}
