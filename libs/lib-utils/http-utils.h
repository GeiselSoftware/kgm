// -*- c++ -*-
#pragma once

#include <string>
#include <utility>
#include <map>

struct HTTPPostRequest
{
  std::string host;
  int port;
  std::string target, body;
};

std::string urlEncode(const std::string& value);
std::string toUrlEncodedForm(const std::map<std::string, std::string>& data);

#ifdef __EMSCRIPTEN__
// wasm build uses emscripten functions to send/receive http post requests
#include <emscripten/fetch.h>

class HTTPRawRequestHandler
{
private:
  static void on_success(emscripten_fetch_t *fetch);
  static void on_error(emscripten_fetch_t *fetch);

  bool request_in_progress = false;
  std::string raw_response;
  
public:
  void send_http_request(const HTTPPostRequest&);
  bool get_response_non_blocking(std::string*);
};

#else
// native build uses worker thread to send/receive http post requests
#include "mt-safe-queue.h"
#include <thread>

class HTTPRawRequestHandler
{
private:
  void send_post_request__(const std::string& server, int port, const std::string& target, const std::string& body);

  ThreadSafeQueue<HTTPPostRequest> request_q;
  ThreadSafeQueue<std::string> response_q;

public:
  std::thread http_req_thread;
  void start();

  void send_http_request(const HTTPPostRequest&);
  bool get_response_non_blocking(std::string*);
};
#endif