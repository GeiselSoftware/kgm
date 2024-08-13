#include <imgui_node_editor_internal.h>
#include <misc/cpp/imgui_stdlib.h>
#include <imgui.h>

#include <lib-utils/string-utils.h>
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
  string kgm_path;
  
  explicit SHACLEditor(const string& fuseki_server_url, const string& kgm_path) :
    rdf_manager(fuseki_server_url),
    vis_manager(&rdf_manager)
  {
    this->fuseki_server_url = fuseki_server_url;
    this->kgm_path = kgm_path;
  }

  void save_graph()
  {
    bool button_disabled = false;
    if (rdf_manager.in_progress_save_graph_f) {
      button_disabled = true;
      ImGui::BeginDisabled(true);
    }

    if (ImGui::Button("test save")) {
      if (!rdf_manager.in_progress_save_graph_f) {
	vector<RDFSPO> triples;
	vis_manager.userclasses_to_triples(&triples);
        rdf_manager.start_save_graph(this->kgm_path, triples);
      }
    }

    if (rdf_manager.in_progress_save_graph_f) {
      rdf_manager.finish_save_graph();
    }

    if (button_disabled) {
      ImGui::EndDisabled();
    }
  }
  
  void load_graph()
  {
    bool button_disabled = false;
    if (rdf_manager.in_progress_load_graph()) {
      button_disabled = true;
      ImGui::BeginDisabled(true);
    }

    static bool done_inital_load_action = false;
    if (ImGui::Button("test load") || done_inital_load_action == false) {
      done_inital_load_action = true;
      if (!rdf_manager.in_progress_load_graph()) {
        rdf_manager.start_load_graph(this->kgm_path);
      }
    }

    if (rdf_manager.in_progress_load_graph()) {
      rdf_manager.finish_load_graph();
      vis_manager.reset();
      vis_manager.build_visnode_classes();
      vis_manager.build_userobjects();
    }

    if (button_disabled) {
      ImGui::EndDisabled();
    }
  }
  
  void ShowLeftPane(float paneWidth)
  {
    auto& io = ImGui::GetIO();
    ImGui::BeginChild("Selection", ImVec2(paneWidth, 0));

    paneWidth = ImGui::GetContentRegionAvail().x;

    if (ImGui::Button("Zoom to Content")) {
      ed::NavigateToContent();
    }

    if (1) { // add new userclass
      if (ImGui::Button("Add new class")) {
	vis_manager.add_new_userclass();
      }
    }
    
    load_graph();
    save_graph();
    
    if (1) { // dump shacl
      if (ImGui::Button("dump shacl")) {
	vis_manager.dump_shacl();
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

#if 1
    // Get main viewport dimensions
    ImGuiViewport* viewport = ImGui::GetMainViewport();
    ImVec2 viewportPos = viewport->Pos;
    ImVec2 viewportSize = viewport->Size;
    // Show main window occupying whole viewport    
    ImGui::SetNextWindowPos(viewportPos);
    ImGui::SetNextWindowSize(viewportSize);    
    ImGui::Begin("Main", 0, ImGuiWindowFlags_NoDecoration);
#else
    ImGui::SetNextWindowPos(ImVec2(0, 0));
    ImGui::SetNextWindowSize(ImVec2(800, 600));
    ImGui::Begin("Main");
#endif
    
    ImGui::Text("%s %s", this->fuseki_server_url.c_str(), this->kgm_path.c_str());
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

    ImGui::End();

    // second window
    //ImGui::SetNextWindowFocus();
    ImGui::Begin("Aux");
    ImGui::BringWindowToDisplayFront(ImGui::GetCurrentWindow());
    ImGui::Text("%s", vis_manager.shacl_dump.c_str());
    //ImGui::ShowMetricsWindow();
    ImGui::End();

  }

};

bool process_wasm_run_args(const char* b64_args, string* fuseki_host, string* fuseki_port, string* kgm_path)
{
  auto args_s = base64_decode(string(b64_args));
  bool fuseki_host_ok = false, fuseki_port_ok = false, kgm_path_ok = false;
  for (auto& arg_pair_s: string_split(args_s, ',')) {
    auto [k, v] = string_split_to_pair(arg_pair_s, '=');
    if (k == "FUSEKI_HOST") {
      *fuseki_host = v;
      fuseki_host_ok = true;
    }
    if (k == "FUSEKI_PORT") {
      *fuseki_port = v;
      fuseki_port_ok = true;
    }
    if (k == "KGM_PATH") {
      *kgm_path = v;
      kgm_path_ok = true;
    }
  }

  return fuseki_host_ok && fuseki_port_ok && kgm_path_ok;
}

int main(int argc, char** argv)
{
  cout << "main args:" << endl;
  for (int i = 0; i < argc; i++) {
    cout << i << " " << argv[i] << endl;
  }
  cout << "--------------------" << endl;

  string fuseki_url, kgm_path;
  
#ifdef __EMSCRIPTEN__
  if (argc != 2) {
    cout << "error - wrong args" << endl;
    exit(2);
  } else {
    string fuseki_host, fuseki_port;
    if (!process_wasm_run_args(argv[1], &fuseki_host, &fuseki_port, &kgm_path)) {
      cout << "error processing args" << endl;
      exit(3);
    }
    cout << "fuseki_host: " << fuseki_host << endl;
    cout << "fuseki_port: " << fuseki_port << endl;
    cout << "kgm_path: " << kgm_path << endl;
    fuseki_url = string("http://") + fuseki_host + ":" + fuseki_port + "/kgm-default-dataset/query";
  }
#else  
  if (argc != 3) {
    cout << "error, need suply url to fuseki server and kgm path to existing graph" << endl;
    cout << "Example: " << argv[0] << " http://metis:3030/kgm-default-dataset/query /NorthWind.shacl" << endl;
    exit(2);
  } else {
    fuseki_url = argv[1];
    kgm_path = argv[2];
  }
#endif

  if (fuseki_url.size() == 0) {
    cout << "no fuseki url specified" << endl;
    exit(2);
  }

  if (kgm_path.size() == 0) {
    cout << "no path to graph is spcified" << endl;
    exit(2);
  }
  
  cout << "fuseki url: " << fuseki_url << endl;
  SHACLEditor e(fuseki_url, kgm_path);
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
