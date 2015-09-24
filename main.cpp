
#include <iostream>
#include <string>
#include <string.h>
#include <vector>
#include <unordered_set>

#include "utils.h"


const char* tag_delim = " ._-+&%%()[]{}";


typedef std::string Tag;
typedef std::unordered_set<Tag> TagSet;

typedef std::string File;
typedef std::unordered_set<File> FileSet;



static TagSet get_tags(std::string f)
{
    std::vector<std::string> tag_list = split(f, tag_delim);

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
                    //must be a file
                    files.insert( File(argv[i]) );
            }
        }

        if(files.size() == 0)
        {
            help();
            return -1;
        }

        run(add_tags, remove_tags, files);
    }

	return 0;
}
