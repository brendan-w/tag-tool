
#pragma once


#include <string>
#include <vector>


#ifdef _WIN32
    const char PATH_SEP = '\\';
#else
    const char PATH_SEP = '/';
#endif


#ifdef _WIN32
  #include <direct.h>
  #define getcwd _getcwd
#else
  #include <unistd.h> //getcwd()
#endif


/*
    used when renaming the file for new tags

    [                   dirs                   ][   name    ][ext]
    /home/brendan/dev/cpp/collector/src/display/displayobject.cpp
*/
typedef struct {
    std::string dirs;
    std::string name;
    std::string ext;
} Path_Parts;


bool dir_exists(const char* path);
bool file_exists(const char* filename);
std::string parent_dir(std::string dir);
std::vector<std::string> split(std::string & str, std::string delims);
std::string path_join(std::string a_str, std::string b_str);
Path_Parts get_path_parts(std::string path);
std::string join_path_parts(Path_Parts p);
