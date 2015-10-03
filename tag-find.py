#!/usr/bin/env python3

import re
import sys
import subprocess
from utils import *
from collections import namedtuple

Operation = namedtuple('TagOp', 'tag type')

# available operations
INTERSECTION = 0
INCLUSION    = 1
EXCLUSION    = 2



help_text = """
Usage:
\ttag-find [OPTION...] [SELECTOR...]

Selectors:
\t[TAG]    filters tagged files for this tag         ("AND")
\t+[TAG]   adds tagged files to the selection        ("OR")
\t-[TAG]   removes tagged files from the selection   ("NOT")

Options:
\t--casei   performs a case insensitive search
\t--help    prints this help text and exits

For issues and documentation: https://github.com/brendanwhitfield/tag-tool
"""




# constructs a find command based on the operations given
# Note: The result of this command will contain several falsely selected
# files, since it will also match substrings of tags.
def build_command(operations):

    find_flags = ""

    # chooses one of the following:
    # -name -iname -path -ipath
    flag = " -"
    flag += "i" if not settings.case_sensitive else ""
    flag += "path" if settings.use_dirs else "name"

    for op in operations:
        if op.type == INCLUSION:
            if not find_flags:
                find_flags += " %s *%s*" % (flag, op.tag)
            else:
                find_flags = "( " + find_flags + " ) -o %s *%s*" % (flag, op.tag)
        elif op.type == EXCLUSION:
            find_flags += " ! %s *%s*" % (flag, op.tag)
        elif op.type == INTERSECTION:
            find_flags += " %s *%s*" % (flag, op.tag)

    # insert the selection flags into the main find command
    return settings.find_cmd % find_flags


# function that uses `find` to retrieve a basic list of files matching
# the given tag selectors.
# Note: see note for build_command()
def find_base_files(operations):

    cmd = build_command(operations)

    # run the find
    try:
        b = subprocess.check_output(cmd.split(), universal_newlines=True)
        return b.split()
    except subprocess.CalledProcessError:
        print("Failed to execute 'find'")
        return []


# returns boolean for whether the file was selected
def match(f, operations):
    path_parts = f_split(f)
    tags = get_all_tags(path_parts)

    matched = True

    # unfortunately, we can't bail on the first unmatched operation
    # since the file can always be included later with `+[TAG]`
    for op in operations:

        if op.type == INTERSECTION:
            if op.tag not in tags:
                matched = False
        else:
            # if the file has the tag for this operation
            if op.tag in tags:
                if op.type == INCLUSION:
                    matched = True
                elif op.type == EXCLUSION:
                    matched = False

    return matched


# function to refine the selection based on the users instructions
# accepts a list of files generated by find_base_files()
def select(operations):
    base_files = find_base_files(operations)
    return [f for f in base_files if match(f, operations)]


def main():
    load_settings()

    operations = []

    for option in sys.argv[1:]:
        if option == "--help":
            print(help_text)
            return
        elif option == "--casei":
            settings.case_sensitive = False
        else:
            if option[0] == "+":
                operations.append(Operation(option[1:], INCLUSION))
            elif option[0] == "-":
                operations.append(Operation(option[1:], EXCLUSION))
            else:
                operations.append(Operation(option, INTERSECTION))

    # check that the user entered something
    if len(operations) == 0:
        print("please give tag selectors")
        return

    # check for delimeters in the tags
    if not all([ valid_tag(op.tag) for op in operations ]):
        print("tags cannot contain delimeters")
        return

    # the get_tags() function lower()s things for case insensitivity
    if not settings.case_sensitive:
        operations = [Operation(tag.lower(), op) for tag, op in operations]

    # run the selection
    files = select(operations)
    for f in files:
        print(f)


if(__name__ == "__main__"):
    main()