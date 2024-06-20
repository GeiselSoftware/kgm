#include <imgui_node_editor_internal.h>
#include <imgui.h>

#include <lib-apploops/loop-runner.h>
#include "vis-node-manager.h"
#include "rdf-node-manager.h"

namespace ed = ax::NodeEditor;

#include <iostream>
#include <sstream>
#include <thread>
using namespace std;

struct Example: public LoopStep
{
  string fuseki_server_url;

  explicit Example(const string& fuseki_server_url) {
    this->fuseki_server_url = fuseki_server_url;
  }
  
  RDFNodeManager rdf_node_manager;
  VisNodeManager vis_node_manager;
  ed::EditorContext* m_Editor = 0;

  void before_loop_starts() override {
#ifndef __EMSCRIPTEN__
    this->rdf_node_manager.http_request_handler.start(); // start http handler thread
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
    
    // Show left window
    ImGui::SetNextWindowPos(viewportPos);
    ImGui::SetNextWindowSize(ImVec2(viewportSize.x * 0.15f, viewportSize.y));
    if (1) {
      ImGui::Begin("Left Window", NULL, ImGuiWindowFlags_NoMove | ImGuiWindowFlags_NoResize | ImGuiWindowFlags_NoCollapse);	
      ImGui::Text("FPS: %.2f (%.2gms)", io.Framerate, io.Framerate ? 1000.0f / io.Framerate : 0.0f);
      ImGui::Separator();	

#if 0
      if (ImGui::Button("add new class")) {
	cout << "add new class pressed" << endl;
	auto new_class_uri = create_classURI(URI{"test"});
	node_manager.nodes.set(new_class_uri, make_shared<RDFSClassNode>(new_class_uri));
      }
#endif
      
      if (ImGui::Button("dump shacl")) {
	cout << "dump shacl" << endl;
	rdf_node_manager.do_dump_shacl();
      }

      { // list of gse graphs
	ImGui::Text("gse graphs");
	vector<string> items = { "/alice-bob/simple", "/alice-bob/simple-shacl", "/alice-bob/KUI" };
        static int item_current_idx = 0; // Here we store our selection data as an index.
        if (ImGui::BeginListBox("##gse-graphs")) {
	  for (int n = 0; n < items.size(); n++) {
	    const bool is_selected = (item_current_idx == n);
	    if (ImGui::Selectable(items[n].c_str(), is_selected)) {
	      item_current_idx = n;
	      cout << "selected: " << items[item_current_idx] << endl;
	    }

	    // Set the initial focus when opening the combo (scrolling + keyboard navigation focus)
	    if (is_selected) {
	      ImGui::SetItemDefaultFocus();
	    }
	  }
	  ImGui::EndListBox();
        }

	if (ImGui::Button("refresh\nlist")) {
	  
	}
	
	ImGui::SameLine();

	{ // load graph
	  bool button_disabled = false;
	  if (rdf_node_manager.in_progress_load_graph()) {
	    button_disabled = true;
	    ImGui::BeginDisabled(true);
	  }

	  if (ImGui::Button("load")) {
	    if (!rdf_node_manager.in_progress_load_graph()) {
	      auto gse_path = items[item_current_idx];
	      rdf_node_manager.start_load_graph(gse_path, this->fuseki_server_url);
	    }
	  }
	  
	  if (rdf_node_manager.in_progress_load_graph()) {
	    rdf_node_manager.finish_load_graph(&this->vis_node_manager);
	  }
	  
	  if (button_disabled) {
	    ImGui::EndDisabled();
	  }
	}
      }
      
      ImGui::End();
    }

    // show right window
    if (1) {
      ImGui::SetNextWindowPos(ImVec2(viewportPos.x + viewportSize.x * 0.15f, viewportPos.y));
      ImGui::SetNextWindowSize(ImVec2(viewportSize.x * 0.85f, viewportSize.y));
      ImGui::Begin("Right Window", NULL, ImGuiWindowFlags_NoMove | ImGuiWindowFlags_NoResize | ImGuiWindowFlags_NoCollapse);
      ImGui::Text("%s", this->fuseki_server_url.c_str());

      ed::SetCurrentEditor(m_Editor);

      ed::Begin("My Editor", ImVec2(0.0, 0.0f));
      this->vis_node_manager.make_frame();
      ed::End();

      //ed::NavigateToContent(0.0f);     

      ed::SetCurrentEditor(nullptr);
      
      ImGui::End();
    }
    // ImGui::ShowMetricsWindow();
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
    fuseki_url = string("http://") + fuseki_host + ":" + fuseki_port + "/gse/";
  }
#else  
  if (argc != 2) {
    cout << "error, need suply url to fuseki server" << endl;
    cout << "Example: " << argv[0] << " http://metis:3030/gse/" << endl;
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
  Example e(fuseki_url);
  LoopRunner lr(&e);

  if (init(&lr) != 0) return 1;
  lr.run();

  quit();

#ifndef __EMSCRIPTEN__
  e.rdf_node_manager.http_request_handler.send_http_request(HTTPPostRequest()); // thread will exit on empty request
  e.rdf_node_manager.http_request_handler.http_req_thread.join(); // wait for above to complete
#endif
  
  cout << "all done, exiting" << endl;
  return 0;
}
