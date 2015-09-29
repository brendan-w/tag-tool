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
tag_delims = "[ \\/.,_&%%\\-\\+\\(\\)\\[\\]\\{\\}]"
default_delim = "_"


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
    if os.path.isfile(os.path.join(path, filename)):
        return path
    else:
        if path == "/":
            return ""
        else:
            return find_above(os.path.dirname(path), filename)


# splits an absolute file into an instance of PathParts
def f_split(f):
    # split out the dirs, the filename, and the extension
    dirs, f   = os.path.split(f)
    name, ext = os.path.splitext(f)

    # if dirs are being used, do NOT consider the path
    # to the root tag directory
    if use_dirs:
        dirs = os.path.relpath(dirs, root_dir)

    return PathParts(dirs, name, ext)


# reassemble a PathParts struct back into a filename
def f_join(path_parts):
    path = path_parts.dirs
    filename = path_parts.name + path_parts.ext

    # if a root dir was used, resolve the reference
    if use_dirs:
        path = os.path.join(root_dir, path)

    return os.path.join(path, filename)


# returns a set of tags on this file
def get_tags(path_parts):
    tags = set(re.split(tag_delims, path_parts.name))

    if use_dirs:
        tags.union(set(re.split(tag_delims, path_parts.dirs)))

    return set(filter(bool, tags)) # strain out empty strings


# adds a tag to this file's name
# if there is a dir to encode this tag, it will be removed from
# the filename in the place() function
def add(tag, path_parts):
    return PathParts(path_parts.dirs,
                     tag + default_delim + path_parts.name,
                     path_parts.ext)


def remove(tag, path_parts):
    name = path_parts.name
    dirs = path_parts.dirs

    # remove tags from the name
    # run as 3 different regexes for simplicity
    front_pattern = "^" + tag + tag_delims
    back_pattern  = tag_delims + tag + "$"
    mid_pattern   = ("(?<=%s)" % tag_delims) + tag + tag_delims

    # erase any tag instances from the name
    name = re.sub(front_pattern, "", name)
    name = re.sub(back_pattern, "", name)
    name = re.sub(mid_pattern, "", name)

    # remove tags from the dirs
    if use_dirs:
        dirs = re.sub(front_pattern, "", dirs)
        dirs = re.sub(back_pattern, "", dirs)
        dirs = re.sub(mid_pattern, "", dirs)

    return PathParts(dirs, name, path_parts.ext)


# Only used if use_dirs == True
# Sinks a file back down the directory tree, according to its tags
# Directories are favored as tag storage. Also handles deletion of tags
# from dir names carrying multiple tags
def resolve_dirs(path_parts):
    return path_parts


def run(add_tags, remove_tags, files):
    for f in files:
        f = os.path.abspath(f)
        print(f)
        path_parts = f_split(f)

        # remove the requested tags
        for tag in remove_tags:
            path_parts = remove(tag, path_parts)

        current_tags = get_tags(path_parts)

        # add the requested tags, if they're not already there
        for tag in add_tags:
            if tag not in current_tags:
                path_parts = add(tag, path_parts)

        # reposition the file in the tree, favoring tags on directories
        if use_dirs:
            path_parts = resolve_dirs(path_parts)

        new_f = f_join(path_parts)
        print(new_f)


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
