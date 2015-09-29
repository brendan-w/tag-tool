#!/usr/bin/env python3

import os
import re
import sys
from collections import namedtuple

PathParts = namedtuple('PathParts', 'dirs name ext')

# options
verbose = True
root_dir = ""
use_dirs = False
#tag_delims = "[ \\.,_-+&%%\\(\\)\\[\\]\\{\\}]"
tag_delims = "[ \\.,_&%%\\-\\+\\(\\)\\[\\]\\{\\}]"


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

# recursively finds the nearest .tagdir file denoting the limit for moving files
def find_above(path, filename):

    f = os.path.join(path, filename)

    if os.path.isfile(f):
        return path
    else:
        if path == "/":
            return ""
        else:
            find_above(os.path.dirname(path), filename)


def remove(tag, path_parts):

    # remove tags from the name

    # run as 3 different regexes for simplicity
    front_pattern = "^" + tag + tag_delims
    back_pattern  = tag_delims + tag + "$"
    mid_pattern   = ("(?<=%s)" % tag_delims) + tag + tag_delims

    print(path_parts.name)

    n = re.sub(front_pattern, "", path_parts.name)
    n = re.sub(back_pattern, "", n)
    n = re.sub(mid_pattern, "", n)

    print(n)

    # remove tags from the dirs
    if use_dirs:
        pass



def run(add_tags, remove_tags, files):
    for f in files:
        f = os.path.abspath(f)

        # split out the dirs, the filename, and the extension
        dirs, f   = os.path.split(f)
        name, ext = os.path.splitext(f)

        path_parts = PathParts(dirs, name, ext)

        for tag in remove_tags:
            remove(tag, path_parts)





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

    root_dir = find_above(os.getcwd(), ".tagdir")
    use_dirs = (root_dir != "") # could eventually be disabled by an option

    # run the tagger
    run(add_tags, remove_tags, files)



if(__name__ == "__main__"):
    main()
