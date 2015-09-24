
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <unordered_set>
#include <stdlib.h> // realpath()

#include "utils.h"


const char* TAG_DELIMS = " ._-+&%%()[]{}";
const char DEFAULT_TAG_DELIM = '_';


typedef std::string Tag;
typedef std::unordered_set<Tag> TagSet;

typedef std::string File;
typedef std::unordered_set<File> FileSet;



static bool file_exists(const char* filename)
{
    std::ifstream fin(filename);
    return fin;
}


static TagSet get_tags(std::string f)
{
    std::vector<std::string> tag_list = split(f, TAG_DELIMS);

    //strain out duplicates
    TagSet tags;
    for(Tag t: tag_list)
        tags.insert(t);

    return tags;
}


static std::string add_tag(std::string str, Tag tag)
{
    return tag + DEFAULT_TAG_DELIM + str;
}


static std::string remove_tag(std::string str, Tag tag)
{
    size_t pos;
    while( (pos = str.find(tag)) != std::string::npos )
    {
        str.erase(pos, tag.length());

        //remove the delimeter
        if(pos >= str.length())
        {
            //this tag was at the end of the filename
            str.erase(pos - 1, 1);
        }
        else
        {
            //this tag was NOT at the end of the filename
            //erase the forward delimeter
            str.erase(pos, 1);
        }
    }

    return str;
}


static void run(TagSet add_tags, TagSet remove_tags, FileSet files)
{
    for(File f : files)
    {
        Path_Parts p = get_path_parts(f);

        //find out what tags this file already has
        TagSet tags = get_tags(p.name);

        //add tags
        for(Tag t : add_tags)
        {
            //if the file doesn't have this tag
            if(tags.find(t) == tags.end())
                p.name = add_tag(p.name, t);
        }

        //remove tags
        for(Tag t : remove_tags)
        {
            //if the file already has this tag
            if(tags.find(t) != tags.end())
                p.name = remove_tag(p.name, t);
        }

        File new_f = join_path_parts(p);

        std::cout << "new name = " << new_f << std::endl;
    }
}


static void help()
{
    std::cout << "\
Usage:\n\
\ttag [COMMAND...] [FILE...]\n\
\n\
Commands:\n\
\t+[TAG]   adds a tag to the given files\n\
\t-[TAG]   removes a tag from the given files\n\
\n\
For issues and documentation: https://github.com/brendanwhitfield/collector\n";
}


int main(int argc, char* argv[])
{
    if(argc <= 2)
    {
        help();
        return -1;
    }
    else
    {
        TagSet add_tags;
        TagSet remove_tags;
        FileSet files;

        for(int i = 1; i < argc; i++)
        {
            //look for a plus or a minus sign
            switch(argv[i][0])
            {
                case '+':
                    add_tags.insert( Tag(argv[i]+1) );
                    break;
                case '-':
                    remove_tags.insert( Tag(argv[i]+1) );
                    add_tags.erase(     Tag(argv[i]+1) ); //dont add AND remove the same tag
                    break;
                default:
                    if(file_exists(argv[i]))
                        files.insert( File( realpath(argv[i], NULL)) );
                    else
                        std::cerr << argv[i] << " is not a file" << std::endl;
            }
        }

        run(add_tags, remove_tags, files);
    }

	return 0;
}
