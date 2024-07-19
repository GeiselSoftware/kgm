#include <imgui_node_editor_internal.h>
#include <imgui.h>

#include <lib-apploops/loop-runner.h>
#include "vis-manager.h"
#include "rdf-manager.h"

namespace ed = ax::NodeEditor;

#include <iostream>
#include <sstream>
#include <thread>
using namespace std;

static bool Splitter(bool split_vertically, float thickness, float* size1, float* size2, float min_size1, float min_size2, float splitter_long_axis_size = -1.0f)
{
  using namespace ImGui;
  ImGuiContext& g = *GImGui;
  ImGuiWindow* window = g.CurrentWindow;
  ImGuiID id = window->GetID("##Splitter");
  ImRect bb;
  bb.Min = window->DC.CursorPos + (split_vertically ? ImVec2(*size1, 0.0f) : ImVec2(0.0f, *size1));
  bb.Max = bb.Min + CalcItemSize(split_vertically ? ImVec2(thickness, splitter_long_axis_size) : ImVec2(splitter_long_axis_size, thickness), 0.0f, 0.0f);
  return SplitterBehavior(bb, id, split_vertically ? ImGuiAxis_X : ImGuiAxis_Y, size1, size2, min_size1, min_size2, 0.0f);
}


struct SHACLEditor: public LoopStep
{
  string fuseki_server_url;

  explicit SHACLEditor(const string& fuseki_server_url) {
    this->fuseki_server_url = fuseki_server_url;
  }

  void ShowLeftPane(float paneWidth)
{
  auto& io = ImGui::GetIO();

  ImGui::BeginChild("Selection", ImVec2(paneWidth, 0));

  paneWidth = ImGui::GetContentRegionAvail().x;

  if (ImGui::Button("Zoom to Content")) {
    ed::NavigateToContent();
  }

  if (1) { // load graph
    bool button_disabled = false;
    if (rdf_manager.in_progress_load_graph()) {
      button_disabled = true;
      ImGui::BeginDisabled(true);
    }

    if (ImGui::Button("test load")) {
      if (!rdf_manager.in_progress_load_graph()) {
	auto kgm_path = "/alice-bob.shacl";
	string kgm_shacl_path = "";
	rdf_manager.start_load_graph(this->fuseki_server_url, kgm_path, kgm_shacl_path);
      }
    }

    if (rdf_manager.in_progress_load_graph()) {
      rdf_manager.finish_load_graph();
      vis_manager.build(&rdf_manager);
    }

    if (button_disabled) {
      ImGui::EndDisabled();
    }
  }
  
  ImGui::EndChild();
}
 
  
  RDFManager rdf_manager;
  VisManager vis_manager;
  ed::EditorContext* m_Editor = 0;

  void before_loop_starts() override {
#ifndef __EMSCRIPTEN__
    this->rdf_manager.http_request_handler.start(); // start http handler thread
#endif
    
    ed::Config config;
    config.SettingsFile = "Simple.json";
    this->m_Editor = ed::CreateEditor(&config);    
    ed::SetCurrentEditor(m_Editor);
  }
  
  void make_frame() override {
    auto& io = ImGui::GetIO();

    // Get main viewport dimensions
    ImGuiViewport* viewport = ImGui::GetMainViewport();
    ImVec2 viewportPos = viewport->Pos;
    ImVec2 viewportSize = viewport->Size;

    // Show main window occupying whole viewport    
    ImGui::SetNextWindowPos(viewportPos);
    ImGui::SetNextWindowSize(viewportSize);

    
    ImGui::Begin("Main", 0, ImGuiWindowFlags_NoDecoration);
    
    ImGui::Text("%s", this->fuseki_server_url.c_str());
    ImGui::SameLine(); ImGui::Text("FPS: %.2f (%.2gms)", io.Framerate, io.Framerate ? 1000.0f / io.Framerate : 0.0f);
    
    ed::SetCurrentEditor(m_Editor);
    
    static float leftPaneWidth  = 400.0f;
    static float rightPaneWidth = 800.0f;
    Splitter(true, 4.0f, &leftPaneWidth, &rightPaneWidth, 50.0f, 50.0f);

    ShowLeftPane(leftPaneWidth - 4.0f);
    ImGui::SameLine(0.0f, 12.0f);

    ed::Begin("My Editor", ImVec2(0.0, 0.0f));
    this->vis_manager.make_frame();
    ed::End();

    //ImGui::ShowMetricsWindow();
    ImGui::End();
  }

};

std::vector<std::string> string_split(std::string str, char splitter = '=')
{
  std::vector<std::string> result;
  std::string current = ""; 
  for (int i = 0; i < str.size(); i++) {
    if (str[i] == splitter) {
      if (current != "") {
	result.push_back(current);
	current = "";
      } 
      continue;
    }
    current += str[i];
  }

  if (current.size() != 0) {
    result.push_back(current);
  }

  return result;
}

int main(int argc, char** argv)
{
  cout << "main args:" << endl;
  for (int i = 0; i < argc; i++) {
    cout << i << " " << argv[i] << endl;
  }
  cout << "--------------------" << endl;

  string fuseki_url;
  
#ifdef __EMSCRIPTEN__
  if (argc != 3) {
    cout << "error" << endl;
    cout << "example: http://h1:8000/apps/shacled/run-shacled.html?fuseki-host=metis&fuseki-port=3030" << endl;
    exit(2);
  } else {
    string fuseki_host = string_split(argv[1], '=')[1];
    string fuseki_port = string_split(argv[2], '=')[1];
    fuseki_url = string("http://") + fuseki_host + ":" + fuseki_port + "/kgm-default-dataset/query";
  }
#else  
  if (argc != 2) {
    cout << "error, need suply url to fuseki server" << endl;
    cout << "Example: " << argv[0] << " http://metis:3030/kgm-default-dataset/query" << endl;
    exit(2);
  } else {
    fuseki_url = argv[1];
  }
#endif

  if (fuseki_url.size() == 0) {
    cout << "no fuseki url specified" << endl;
    exit(2);
  }
  
  cout << "fuseki url: " << fuseki_url << endl;
  SHACLEditor e(fuseki_url);
  LoopRunner lr(&e);

  if (init(&lr) != 0) return 1;
  lr.run();

  quit();

#ifndef __EMSCRIPTEN__
  e.rdf_manager.http_request_handler.send_http_request(HTTPPostRequest()); // thread will exit on empty request
  e.rdf_manager.http_request_handler.http_req_thread.join(); // wait for above to complete
#endif
  
  cout << "all done, exiting" << endl;
  return 0;
}
