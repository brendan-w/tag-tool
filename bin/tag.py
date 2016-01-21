#!/usr/bin/env python3

import os
import re
import sys

from tagtool import Filename


verbose = False

help_text = """
Usage:
\ttag [OPTION...] [COMMAND...] [FILE...]

Commands:
\t+[TAG]   adds a tag to the given files
\t-[TAG]   removes a tag from the given files

Options:
\t--nocase     performs case insensitive tag removal
\t--verbose   prints the new filepath for each renamed file
\t--help      prints this help text and exits

For issues and documentation: https://github.com/brendanwhitfield/tag-tool
"""


def run(files, add_tags, remove_tags, config):
    for filestr in files:

        f = Filename(filestr, config)
        f.add_remove_tags(add_tags, remove_tags) # run the tagger
        os.rename(filestr, str(f))

        if verbose:
            print("‘%s’ -> ‘%s’" % (filestr, str(f)))


def main():
    global verbose

    add_tags    = set()
    remove_tags = set()
    files       = set()

    # config params that will override the .tagdir params
    config = {}

    for option in sys.argv[1:]:
        if option == "--help":
            print(help_text)
            return
        elif option == "--verbose":
            verbose = True
        elif option == "--nocase":
            config["case_sensitive"] = False
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
    run(files, add_tags, remove_tags, config)

if(__name__ == "__main__"):
    main()
