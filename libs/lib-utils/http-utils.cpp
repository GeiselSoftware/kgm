#include "http-utils.h"
#include <unistd.h>
#include <arpa/inet.h>
#include <thread>
#include <iostream>
#include <sstream>
#include <iomanip>
using namespace std;

#include "http-utils.h"

std::string urlEncode(const std::string &value)
{
  std::ostringstream escaped;
  escaped.fill('0');
  escaped << std::hex;

  for (char c : value) {
    // Keep alphanumeric characters and other safe characters
    if (isalnum(c) || c == '-' || c == '_' || c == '.' || c == '~') {
      escaped << c;
    } else {
      // Any other characters are percent-encoded
      escaped << '%' << std::setw(2) << int((unsigned char)c);
    }
  }

  return escaped.str();
}

std::string toUrlEncodedForm(const std::map<std::string, std::string> &data)
{
  std::string encoded;
  for (const auto &pair : data) {
    if (!encoded.empty()) {
      encoded += "&";
    }
    encoded += urlEncode(pair.first) + "=" + urlEncode(pair.second);
  }
  return encoded;
}

#ifdef __EMSCRIPTEN__
#include <emscripten/emscripten.h>

void HTTPRawRequestHandler::on_success(emscripten_fetch_t *fetch)
{
  //delete [] fetch->__attributes.requestData; // that was in place in old version of fuseki http handler on wasm
  auto that = reinterpret_cast<HTTPRawRequestHandler*>(fetch->userData);
  std::cout << "POST request succeeded!" << std::endl;
  std::cout << "Fetched " << fetch->numBytes << " bytes from URL: " << fetch->url << std::endl;
  that->raw_response = string(fetch->data, fetch->numBytes);
  that->request_in_progress = false;
  emscripten_fetch_close(fetch);
}

void HTTPRawRequestHandler::on_error(emscripten_fetch_t *fetch)
{
  //delete [] fetch->__attributes.requestData; // that was in place in old version of fuseki http handler on wasm
  auto that = reinterpret_cast<HTTPRawRequestHandler*>(fetch->userData);
  that->raw_response = "";
  that->request_in_progress = false;
  emscripten_fetch_close(fetch);
}

void HTTPRawRequestHandler::send_http_request(const HTTPPostRequest& req)
{
  emscripten_fetch_attr_t attr;
  emscripten_fetch_attr_init(&attr);
  attr.attributes = EMSCRIPTEN_FETCH_LOAD_TO_MEMORY;
  strcpy(attr.requestMethod, "POST");
  char* postData_buf = new char[req.body.size()+1];
  strcpy(postData_buf, req.body.c_str());
  attr.requestData = postData_buf;
  attr.requestDataSize = req.body.size();
	
  auto requestHeaders = { // std::initializer_list<const char *>
    "Content-Type", "application/x-www-form-urlencoded",
    (const char*)0 };
  for (auto rq: requestHeaders) {
    cout << "rq: " << rq << endl;
  }
  cout << "------" << endl;
  
  attr.requestHeaders = requestHeaders.begin();
  attr.onsuccess = HTTPRawRequestHandler::on_success;
  attr.onerror = HTTPRawRequestHandler::on_error;
  attr.userData = this;
  string url = "http://" + req.host + ":" + to_string(req.port) + req.target;
  //string url = "http://h1:3030/ds/";
  this->request_in_progress = true;
  emscripten_fetch(&attr, url.c_str());
}

bool HTTPRawRequestHandler::get_response_non_blocking(std::string* raw_response)
{
  bool ret = false;
  if (this->request_in_progress) {
    ret = false;
  } else if (this->raw_response.size() > 0) {
    ret = true;
    *raw_response = this->raw_response;
    this->raw_response = "";
  }
  return ret;
}

#else
#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>

// from https://stackoverflow.com/a/52728208
static int OpenConnection(const char *hostname, int port)
{
  int sd;
  struct addrinfo hints = {}, *addrs;
  char port_str[16] = {};
  
  hints.ai_family = AF_INET; 
  hints.ai_socktype = SOCK_STREAM;
  hints.ai_protocol = IPPROTO_TCP;
  
  int err = getaddrinfo(hostname, to_string(port).c_str(), &hints, &addrs);
  if (err != 0) {
    throw runtime_error("getaddrinfo() failed"); //fprintf(stderr, "%s: %s\n", hostname, gai_strerror(err));
  }

  for(struct addrinfo *addr = addrs; addr != NULL; addr = addr->ai_next) {
    sd = socket(addr->ai_family, addr->ai_socktype, addr->ai_protocol);
    if (sd == -1) {
      err = errno;
      break; // if using AF_UNSPEC above instead of AF_INET/6 specifically,
      // replace this 'break' with 'continue' instead, as the 'ai_family'
      // may be different on the next iteration...
    }

    if (connect(sd, addr->ai_addr, addr->ai_addrlen) == 0) {
      break;
    }

    err = errno;

    close(sd);
    sd = -1;
  }

  freeaddrinfo(addrs);

  if (sd == -1) {
    throw runtime_error("can't connect"); //fprintf(stderr, "%s: %s\n", hostname, strerror(err));
  }

  return sd;
}

void HTTPRawRequestHandler::send_post_request__(const std::string& server, int port, const std::string& target, const std::string& body)
{ 
  int sock = OpenConnection(server.c_str(), port);
  
  std::string request = "POST " + target + " HTTP/1.1\r\n";
  request += "Host: " + server + "\r\n";
  request += "User-Agent: curl/7.81.0\r\n";
  request += "Accept: */*\r\n";
  request += "Content-Type: application/x-www-form-urlencoded\r\n";
  //request += "Accept-Encoding: gzip, deflate\r\n";
  //request += "Accept-Encoding: deflate\r\n";
  request += "Content-Length: " + std::to_string(body.length()) + "\r\n";
  request += "Connection: close\r\n\r\n";
  request += body;

  send(sock, request.c_str(), request.length(), 0);

  char buffer[1024] = {0};
  std::string response;

  while (true) {
    ssize_t bytes_received = recv(sock, buffer, sizeof(buffer) - 1, 0);
    if (bytes_received <= 0) break;
    buffer[bytes_received] = '\0';
    response += buffer;
  }

  close(sock);

  // Call the callback function with the response
  this->response_q.put(response);
}

void HTTPRawRequestHandler::start()
{
  this->http_req_thread = std::thread([this]() {
    while (true) {
      auto req_o = this->request_q.get();
      if (req_o.host == "") {
	cout << "exiting http req thread" << endl;
	break;
      }
      this->send_post_request__(req_o.host, req_o.port, req_o.target, req_o.body);
    }
  });
}

void HTTPRawRequestHandler::send_http_request(const HTTPPostRequest& req)
{
  this->request_q.put(req);
}

bool HTTPRawRequestHandler::get_response_non_blocking(std::string* raw_response)
{
  string full_raw_response;
  bool ret = this->response_q.try_get(full_raw_response);
  if (ret) {
    auto start_idx = full_raw_response.find("\r\n\r\n");
    *raw_response = full_raw_response.substr(start_idx + 4);
  }
  return ret;
}
#endif