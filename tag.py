#!/usr/bin/env python3

import os
import re
import sys
from file import File
from utils import *


help_text = """
Usage:
\ttag [OPTION...] [COMMAND...] [FILE...]

Commands:
\t+[TAG]   adds a tag to the given files
\t-[TAG]   removes a tag from the given files

Options:
\t--casei     performs case insensitive tag removal
\t--verbose   prints the new filepath for each renamed file
\t--help      prints this help text and exits

For issues and documentation: https://github.com/brendanwhitfield/tag-tool
"""


def run(add_tags, remove_tags, files):
    for filestr in files:
        print(filestr)
        f = File(filestr)
        f.add_remove_tags(add_tags, remove_tags)
        print(str(f))


def main():
    add_tags    = set()
    remove_tags = set()
    files       = set()

    for option in sys.argv[1:]:
        if option == "--help":
            print(help_text)
            return
        elif option == "--verbose":
            settings.verbose = True
        elif option == "--casei":
            settings.case_sensitive = False
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

    # check for delimeters in the tags
    if not all([ valid_tag(tag) for tag in add_tags ]) or \
       not all([ valid_tag(tag) for tag in remove_tags ]):
        print("tags cannot contain delimeters")
        return

    # the get_tags() function lower()s things for case insensitivity
    if not settings.case_sensitive:
        remove_tags = set([tag.lower() for tag in remove_tags])

    # run the tagger
    run(add_tags, remove_tags, files)

if(__name__ == "__main__"):
    main()
