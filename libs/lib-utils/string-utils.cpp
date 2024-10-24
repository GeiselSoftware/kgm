#include "string-utils.h"

using namespace std;

std::pair<std::string, std::string> string_split_to_pair(std::string str, char splitter)
{
  std::pair<std::string, std::string> result;
  auto idx = str.find(splitter);
  if (idx != string::npos) {
    result = make_pair(str.substr(0, idx), str.substr(idx+1));
  } else {
    result = make_pair(str, "");
  }

  return result;
}

std::vector<std::string> string_split(std::string str, char splitter)
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

// from https://stackoverflow.com/a/180949

static const std::string base64_chars =
  "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
  "abcdefghijklmnopqrstuvwxyz"
  "0123456789+/";


static inline bool is_base64(unsigned char c) {
  return (isalnum(c) || (c == '+') || (c == '/'));
}

std::string base64_decode(std::string const& encoded_string)
{
  int in_len = encoded_string.size();
  int i = 0;
  int j = 0;
  int in_ = 0;
  unsigned char char_array_4[4], char_array_3[3];
  std::string ret;

  while (in_len-- && ( encoded_string[in_] != '=') && is_base64(encoded_string[in_])) {
    char_array_4[i++] = encoded_string[in_]; in_++;
    if (i ==4) {
      for (i = 0; i <4; i++)
	char_array_4[i] = base64_chars.find(char_array_4[i]);

      char_array_3[0] = (char_array_4[0] << 2) + ((char_array_4[1] & 0x30) >> 4);
      char_array_3[1] = ((char_array_4[1] & 0xf) << 4) + ((char_array_4[2] & 0x3c) >> 2);
      char_array_3[2] = ((char_array_4[2] & 0x3) << 6) + char_array_4[3];

      for (i = 0; (i < 3); i++)
	ret += char_array_3[i];
      i = 0;
    }
  }

  if (i) {
    for (j = i; j <4; j++)
      char_array_4[j] = 0;

    for (j = 0; j <4; j++)
      char_array_4[j] = base64_chars.find(char_array_4[j]);

    char_array_3[0] = (char_array_4[0] << 2) + ((char_array_4[1] & 0x30) >> 4);
    char_array_3[1] = ((char_array_4[1] & 0xf) << 4) + ((char_array_4[2] & 0x3c) >> 2);
    char_array_3[2] = ((char_array_4[2] & 0x3) << 6) + char_array_4[3];

    for (j = 0; (j < i - 1); j++) ret += char_array_3[j];
  }

  return ret;
}


// from https://stackoverflow.com/a/29962178

string urlEncode(string str)
{
  string new_str = "";
  char c;
  int ic;
  const char* chars = str.c_str();
  char bufHex[10];
  int len = str.size(); //strlen(chars);

  for(int i=0;i<len;i++){
    c = chars[i];
    ic = c;
    // uncomment this if you want to encode spaces with +
    /*if (c==' ') new_str += '+';   
      else */if (isalnum(c) || c == '-' || c == '_' || c == '.' || c == '~') new_str += c;
    else {
      sprintf(bufHex,"%X",c);
      if(ic < 16) 
	new_str += "%0"; 
      else
	new_str += "%";
      new_str += bufHex;
    }
  }
  return new_str;
}

string urlDecode(string str)
{
  string ret;
  char ch;
  int i, ii, len = str.length();

  for (i=0; i < len; i++){
    if(str[i] != '%'){
      if(str[i] == '+')
	ret += ' ';
      else
	ret += str[i];
    }else{
      sscanf(str.substr(i + 1, 2).c_str(), "%x", &ii);
      ch = static_cast<char>(ii);
      ret += ch;
      i = i + 2;
    }
  }
  return ret;
}
