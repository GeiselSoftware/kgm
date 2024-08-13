#pragma once

#include <string>
#include <vector>

std::vector<std::string> string_split(std::string str, char splitter = '=');
std::pair<std::string, std::string> string_split_to_pair(std::string str, char splitter = '=');					       
std::string base64_decode(std::string const& encoded_string);
