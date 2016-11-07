

import subprocess
from collections import namedtuple

from .filename import Filename


# Tag operation struct with slots for the tag (string) and the
# operation type (see below)
Operation = namedtuple('TagOp', 'tag type')

# available operations
INTERSECTION = 0
INCLUSION    = 1
EXCLUSION    = 2




# constructs a find command based on the operations given
# Note: The result of this command will contain several falsely selected
# files, since it will also match substrings of tags.
def build_command(operations, config):

    find_flags = ""

    # chooses one of the following:
    # -name -iname -path -ipath
    flag = " -"
    flag += "i" if not config["case_sensitive"] else ""
    flag += "path" if config["use_dirs"] else "name"

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

    #                 root_dir          find_flags
    find_cmd = ["find"]
    find_cmd += [config["root_dir"]]
    find_cmd += ["-type", "f"]
    find_cmd += find_flags.split()
    find_cmd += ["!", "(", "-path", "*/.*", "-perm", "-o=x", ")"]

    return find_cmd


# function that uses `find` to retrieve a basic list of files matching
# the given tag selectors.
# Note: see note for build_command()
def find_base_files(operations, config):

    cmd = build_command(operations, config)

    # run the find
    try:
        b = subprocess.check_output(cmd, universal_newlines=True)
        return b.splitlines()
    except subprocess.CalledProcessError:
        print("Failed to execute 'find'")
        return []


# function to refine the selection based on the users instructions
# returns boolean for whether the file was selected
def match(f, operations, config):

    matched = True

    # unfortunately, we can't bail on the first unmatched operation
    # since the file can always be included later with `+[TAG]`
    for op in operations:

        if op.type == INTERSECTION:
            if not f.has_tag(op.tag):
                matched = False
        else:
            # if the file has the tag for this operation
            if f.has_tag(op.tag):
                if op.type == INCLUSION:
                    matched = True
                elif op.type == EXCLUSION:
                    matched = False

    return matched


# main selector function
# runs a `find` command and then refines the search with tag matching
def select(operations, config):
    base_files = find_base_files(operations, config)
    return [f for f in base_files if match(Filename(f, config), operations, config)]
