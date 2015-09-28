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


def main():
    global verbose
    global root_dir
    global use_dirs

    add_tags    = []
    remove_tags = []
    files       = []

    for option in sys.argv:
        if option == "--help":
            print(help_text)
            return
        elif option == "--verbose":
            verbose = True
        else:
            if option[1] == "+":
                add_tags.append(option[1:]);
            elif option[1] == "-":
                remove_tags.append(option[1:]);
            elif os.path.isfile(option):
                files.append(option)
            else:
                print("'%s' is not a valid file or command line option" % option)

    if len(files) == 0:
        print("please specify files to be tagged")
        return        

    if (len(add_tags) + len(remove_tags)) == 0:
        print("please specify a tag operation")
        return


if(__name__ == "__main__"):
    main()
