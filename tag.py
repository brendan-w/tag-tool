#!/usr/bin/env python3

import os
import re
import sys


# options
verbose = True
root_dir = ""
use_dirs = False

help_text = """
Usage:
\ttag [OPTION...] [COMMAND...] [FILE...]

Commands:
\t+[TAG]   adds a tag to the given files
\t-[TAG]   removes a tag from the given files

Options:
\t--verbose   prints the new filepath for each renamed file
\t--help      prints this help text and exits

For issues and documentation: https://github.com/brendanwhitfield/tag-tool
"""




def run(add_tags, remove_tags, files):
    for f in files:
        f = os.path.abspath(f)

        # split out the dirs, the filename, and the extension
        dirs, f   = os.path.split(f)
        name, ext = os.path.splitext(f)

        print(dirs)
        print(name)
        print(ext)




def main():
    global verbose
    global root_dir
    global use_dirs

    add_tags    = set()
    remove_tags = set()
    files       = set()

    for option in sys.argv[1:]:
        if option == "--help":
            print(help_text)
            return
        elif option == "--verbose":
            verbose = True
        else:
            if option[0] == "+":
                add_tags.add(option[1:]);
            elif option[0] == "-":
                remove_tags.add(option[1:]);
            elif os.path.isfile(option):
                files.add(option)
            else:
                print("'%s' is not a valid file or command line option" % option)

    if len(files) == 0:
        print("please specify files to be tagged")
        return        

    if (len(add_tags) + len(remove_tags)) == 0:
        print("please specify a tag operation")
        return

    # run the tagger
    run(add_tags, remove_tags, files)



if(__name__ == "__main__"):
    main()
