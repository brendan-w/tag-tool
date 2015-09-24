
#include <iostream>
#include <string>
#include <string.h> // strcmp()
#include <vector>
#include <unordered_set>
#include <stdlib.h> // realpath()

#include "utils.h"


bool verbose = false;


const char* TAG_DELIMS = " ._-+&%%()[]{}";
const char DEFAULT_TAG_DELIM = '_';


typedef std::string Tag;
typedef std::unordered_set<Tag> TagSet;

typedef std::string File;
typedef std::unordered_set<File> FileSet;



static bool move_file(File path, File dest)
{
    //look for a collision
    if(file_exists(dest.c_str()))
    {
        //as long as there's a collision, try adding "(i)" to the filename
        Path_Parts p = get_path_parts(dest);

        size_t i = 1;
        std::string new_dest;

        do
        {
            Path_Parts new_p = p;
            p.name += "(" + std::to_string(i) + ")";
            new_dest = join_path_parts(new_p);
            i++;
        }
        while(file_exists(new_dest.c_str()));

        dest = new_dest;
    }

    //try the rename
    if(rename(path.c_str(), dest.c_str()))
    {
        //failure
        perror(path.c_str());
        return false;
    }

    if(verbose)
        std::cout << dest << std::endl;

    return true;
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
        if(str.length() > 0)
        {
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
    }

    return str;
}

//this function assumes that add_tags and remove_tags are
//disjoint sets, and that all files exist
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

        if(p.name == "")
            p.name = "unknown";

        File new_f = join_path_parts(p);

        if(f != new_f)
            move_file(f, new_f);
    }
}


static void help()
{
    std::cout << "\
Usage:\n\
\ttag [OPTION...] [COMMAND...] [FILE...]\n\
\n\
Commands:\n\
\t+[TAG]   adds a tag to the given files\n\
\t-[TAG]   removes a tag from the given files\n\
\n\
Options:\n\
\t--verbose   prints the new filepath for each renamed file\n\
\t--help      prints this help text and exits\n\
\n\
For issues and documentation: https://github.com/brendanwhitfield/tag-tool\n";
}


int main(int argc, char* argv[])
{
    if(argc < 3) //3 is the min number of args for something to happen
    {
        help();
        return 0;
    }

    TagSet add_tags;
    TagSet remove_tags;
    FileSet files;

    //parse command line arguments
    for(int i = 1; i < argc; i++)
    {
        //look for option switches
        if(strcmp(argv[i], "--help") == 0)
        {
            help();
            return 0;
        }
        else if(strcmp(argv[i], "--verbose") == 0)
        {
            verbose = true;
        }
        else
        {
            //look for a plus or a minus sign, denoting tag operations
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
    }

    //check if any files were specified
    if(files.size() == 0)
    {
        std::cerr << "Please specify files to be tagged (use --help for more info)" << std::endl;
        return -1;
    }

    //check if any tag operations were specified
    if(add_tags.size() + remove_tags.size() == 0)
    {
        std::cerr << "Please specify a tag operation (use --help for more info)" << std::endl;
        return -1;
    }

    //tag the files
    run(add_tags, remove_tags, files);

	return 0;
}
