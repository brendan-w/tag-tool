#!/usr/bin/env python3


import sys
import subprocess
from collections import namedtuple

Operation = namedtuple('TagOp', 'tag type')

# available operations
INTERSECTION = 0
INCLUSION    = 1
EXCLUSION    = 2


find_cmd = "find . -type f %s ! -path */.* ! -perm -o=x";



help_text = """
Usage:
\ttag-find [OPTION...] [SELECTOR...]

Selectors:
\t[TAG]    filters tagged files for this tag         ("AND")
\t+[TAG]   adds tagged files to the selection        ("OR")
\t-[TAG]   removes tagged files from the selection   ("NOT")

Options:
\t--help   prints this help text and exits

For issues and documentation: https://github.com/brendanwhitfield/tag-tool
"""


# function that uses `find` to retrieve a basic list of files matching
# the given tag selectors.
# Note: This list will contain several falsely selected files, since it
# will also match substrings of tags.
def find_base_files(operations):

    # construct the find command based on the operations given
    cmd_str = ""

    for op in operations:
        if op.type == INCLUSION:
            cmd_str += " -path *%s*" % op.tag
        elif op.type == EXCLUSION:
            cmd_str += " ! -path *%s*" % op.tag

    # insert the selection flags into the find command
    cmd = find_cmd % cmd_str

    # run the find
    try:
        b = subprocess.check_output(cmd.split(), universal_newlines=True)
        files = b.split()
        return files
    except subprocess.CalledProcessError:
        print("Failed to execute 'find'")
        return []


def run(operations):
    print(find_base_files(operations))


def main():

    operations = []

    # the 3 types of selection operations

    tag_intersections = set()
    tag_additions     = set()
    tag_exclusions    = set()

    for option in sys.argv[1:]:
        if option == "--help":
            print(help_text)
            return
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

    # run the selection
    run(operations)


if(__name__ == "__main__"):
    main()
