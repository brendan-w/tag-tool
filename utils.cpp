
#include "utils.h"


std::vector<std::string> split(std::string & str, std::string delims)
{
    std::vector<std::string> parts;

    size_t prev = 0;
    size_t pos = 0;

    //while there is another delimeter
    while((pos = str.find_first_of(delims, prev)) != std::string::npos)
    {
        if(pos > prev)
            parts.push_back(str.substr(prev, pos-prev));

        prev = pos + 1;
    }

    //add the last tag to the set
    if(prev < str.length())
        parts.push_back(str.substr(prev, std::string::npos));

    return parts;
}

std::string path_join(std::string a_str, std::string b_str)
{
    bool a = (a_str.back() == PATH_SEP);
    bool b = (b_str.front() == PATH_SEP);

    if(a && b)
        a_str.pop_back();
    else if(!a && !b)
        a_str.push_back(PATH_SEP);

    return a_str + b_str;
}

Path_Parts get_path_parts(std::string path)
{
    //split the filepath into directories and file name
    Path_Parts p;
    p.dirs = "";
    p.name = path;
    p.ext = "";

    size_t last_dir = p.name.rfind(PATH_SEP);

    if(last_dir != std::string::npos)
    {
        last_dir++; //include the PATH_SEP in the dirs portion, and not the name
        p.dirs = p.name.substr(0, last_dir);
        p.name = p.name.substr(last_dir);
    }

    size_t ext_pos = p.name.rfind(".");

    if(ext_pos != std::string::npos)
    {
        p.ext  = p.name.substr(ext_pos);
        p.name = p.name.substr(0, ext_pos);
    }

    return p;
}

std::string join_path_parts(Path_Parts p)
{
    return path_join(p.dirs, p.name + p.ext);
}
