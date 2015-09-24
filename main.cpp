
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
            {
                p.name = t + DEFAULT_TAG_DELIM + p.name;
            }
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
