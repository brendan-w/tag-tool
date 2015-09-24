
#include <iostream>
#include <string>
#include <string.h>
#include <vector>
#include <unordered_set>


typedef std::string Tag;
typedef std::unordered_set<Tag> TagSet;

typedef std::string File;
typedef std::unordered_set<File> FileSet;




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

static void add_tag(std::string tag, std::string filepath)
{
    std::cout << filepath << std::endl;
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
    }

	return 0;
}
