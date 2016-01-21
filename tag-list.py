#!/usr/bin/env python3

import os
import re
import sys
from core import *


help_text = """
Usage:
\ttag-list [OPTION...] [FILE...]

Options:
\t--nocase     performs case insensitive tag removal
\t--help      prints this help text and exits

For issues and documentation: https://github.com/brendanwhitfield/tag-tool
"""


def run(files):

    tags = set()

    for filestr in files:
        f = File(filestr)
        tags.update(f.get_tags())
        os.rename(filestr, str(f))

    for tag in tags:
        print(tag)


def main():
    files = set()

    for option in sys.argv[1:]:
        if option == "--help":
            print(help_text)
            return
        elif option == "--nocase":
            settings.case_sensitive = False
        elif os.path.isfile(option):
            files.add(option)
        else:
            print("'%s' is not a valid file" % option)

    if len(files) == 0:
        print("please specify files to list")
        return        

    # run the tagger
    run(files)

if(__name__ == "__main__"):
    main()
