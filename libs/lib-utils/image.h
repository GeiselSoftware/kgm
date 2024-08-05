#include <GL/gl.h>

bool LoadTextureFromFile(const char* filename, GLuint* out_texture, int* out_width, int* out_height);
GLuint LoadTextureFromMemory(const unsigned char* image_data, int image_size);

