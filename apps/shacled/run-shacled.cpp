#include <imgui_node_editor_internal.h>
#include <imgui.h>

#include <lib-apploops/loop-runner.h>
#include "node-manager.h"
#include "rdfsclass-node.h"
#include "http-utils.h"
#include "fuseki-utils.h" // for test call

namespace ed = ax::NodeEditor;

#include <iostream>
#include <sstream>
#include <thread>
using namespace std;

struct Example: public LoopStep
{
  NodeManager node_manager;
  ed::EditorContext* m_Editor = 0;

  HTTPRawRequestHandler http_request_handler;
  bool http_req_in_progress = false;
  
  void before_loop_starts() override {
#ifndef __EMSCRIPTEN__
    this->http_request_handler.start(); // start http handler thread
#endif
    
    ed::Config config;
    config.SettingsFile = "Simple.json";
    this->m_Editor = ed::CreateEditor(&config);    
    ed::SetCurrentEditor(m_Editor);

#if 0
    node_manager.nodes.push_back(node_manager->create_RDFSClassNode("Node A"));
    ed::SetNodePosition(node_manager.nodes.back()->ID, ImVec2(10, 10));
    node_manager.nodes.push_back(node_manager->create_RDFSClassNode("Node B"));
    ed::SetNodePosition(node_manager.nodes.back()->ID, ImVec2(210, 60));
#endif
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
      
      if (ImGui::Button("add new class")) {
	cout << "add new class pressed" << endl;
	node_manager.nodes.push_back(node_manager.create_RDFSClassNode());
      }

      if (ImGui::Button("dump shacl")) {
	cout << "dump shacl" << endl;
	node_manager.do_dump_shacl();
      }

      bool button_disabled = false;
      if (this->http_req_in_progress) {
	button_disabled = true;
	ImGui::BeginDisabled(true);
      }
      
      if (ImGui::Button("load test json")) {
	this->http_req_in_progress = true;
	string rq = "select ?s ?p ?o { ?s ?p ?o }";	
	HTTPPostRequest req{"h1", 3030, "/ds/", toUrlEncodedForm(map<string, string>{{"query", rq}})};
	this->http_request_handler.send_http_request(req);
      }
      
      string raw_response;
      if (this->http_request_handler.get_response_non_blocking(&raw_response) == true) {
	if (raw_response.size() > 0) {
	  //cout << raw_response << endl;
	  node_manager.load_json(raw_response.c_str());
	}
	this->http_req_in_progress = false;
      }

      if (button_disabled) {
	ImGui::EndDisabled();
      }
      
      ImGui::End();
    }

    // show right window
    if (1) {
      ImGui::SetNextWindowPos(ImVec2(viewportPos.x + viewportSize.x * 0.15f, viewportPos.y));
      ImGui::SetNextWindowSize(ImVec2(viewportSize.x * 0.85f, viewportSize.y));
      ImGui::Begin("Right Window", NULL, ImGuiWindowFlags_NoMove | ImGuiWindowFlags_NoResize | ImGuiWindowFlags_NoCollapse);

      ed::SetCurrentEditor(m_Editor);

      ed::Begin("My Editor", ImVec2(0.0, 0.0f));
      this->node_manager.make_frame();
      ed::End();

      //ed::NavigateToContent(0.0f);     

      ed::SetCurrentEditor(nullptr);
      
      ImGui::End();
    }
    // ImGui::ShowMetricsWindow();
  }

};


int main(int argc, char** argv)
{
  Example e;  
  LoopRunner lr(&e);

  if (init(&lr) != 0) return 1;
  lr.run();

  quit();

#ifndef __EMSCRIPTEN__
  e.http_request_handler.send_http_request(HTTPPostRequest()); // thread will exit on empty request
  e.http_request_handler.http_req_thread.join(); // wait for above to complete
#endif
  
  cout << "all done, exiting" << endl;
  return 0;
}
