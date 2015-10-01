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
no_tags_filename = "unknown"


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

# testing harness for changing settings
def test_options(root, dirs):
    global root_dir
    global use_dirs
    root_dir = root
    use_dirs = dirs


# recursively finds the nearest .tagdir file denoting the limit for moving files
def find_above(path, filename):
    if os.path.isfile(os.path.join(path, filename)):
        return path
    else:
        if path == "/":
            return ""
        else:
            return find_above(os.path.dirname(path), filename)


# lists only directories at the given path
def dirs_at(path):
    return [ name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name)) ]


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


# returns the tagset for an arbitrary string
def get_tags(s):
    tags = set(re.split(tag_delims, s))
    return set(filter(bool, tags)) # strain out empty strings


# returns a set of tags on this file
def get_all_tags(path_parts):
    tags = get_tags(path_parts.name)

    if use_dirs:
        tags.union(get_tags(path_parts.dirs))

    return tags


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
    # run as different regexes for simplicity
    mid_pattern   = ("(?<=%s)" % tag_delims) + tag + tag_delims
    front_pattern = "^" + tag + tag_delims
    back_pattern  = tag_delims + tag + "$"
    only_pattern  = "^" + tag + "$"

    # erase any tag instances from the name

    # WARNING: the order here is important. Deleting tags from the front or the
    # back will cause inner tags to become front or back tags. This causes
    # problems if there are two of the same tag adjacent to one-another.
    name = re.sub(mid_pattern, "", name)
    name = re.sub(front_pattern, "", name)
    name = re.sub(back_pattern, "", name)
    name = re.sub(only_pattern, no_tags_filename, name)

    # remove tags from the dirs
    if use_dirs:
        dirs = re.sub(mid_pattern, "", dirs)
        dirs = re.sub(front_pattern, "", dirs)
        dirs = re.sub(back_pattern, "", dirs)
        dirs = re.sub(only_pattern, "", dirs)

    return PathParts(dirs, name, path_parts.ext)


# recursive function that determines the filepath that encodes the most
# of the given tagset.
def find_best_path(path, tags):

    best_path = path
    best_tags_left = set(tags) # goal is to minimize len() for this

    # search all of the directories at the current path
    for d in dirs_at(os.path.join(root_dir, path)):

        d_tags = get_tags(d)

        # if the tags of the directory name are all tags that we're looking for
        if all([t in tags for t in d_tags]):
            # we've found a valid dir to put the file in
            
            # prepare to recurse by removing the tags consumed by this dir name
            next_tags = set(tags).difference(d_tags)

            # recurse
            r = find_best_path(os.path.join(path, d), next_tags)

            # check to see if a better score was achieved
            if(len(r[1]) < len(best_tags_left)):
                best_path      = r[0]
                best_tags_left = r[1]

        # skip directories that contain tags we AREN'T looking for 

    return (best_path, best_tags_left)


# Only used if use_dirs == True
# Sinks a file back down the directory tree, according to its tags
# Directories are favored as tag storage. Also handles deletion of tags
# from dir names carrying multiple tags
def resolve_dirs(path_parts):
    tags = get_all_tags(path_parts)

    # recurse to find the best directory path for this tagset
    path, remaining_tags = find_best_path(root_dir, tags)

    # find out which tags were handled by directories
    # and remove them from the filename
    for tag in tags.difference(remaining_tags):
        path_parts = remove(tag, path_parts)

    return PathParts(path, path_parts.name, path_parts.ext)


# parses tags for a single file, and returns a new filename
def run_for_file(add_tags, remove_tags, f):
    # return "/home/brendan/tag-tool/unknown.txt"
    path_parts = f_split(f)

    # remove the requested tags
    for tag in remove_tags:
        path_parts = remove(tag, path_parts)

    current_tags = get_all_tags(path_parts)

    # add the requested tags, if they're not already there
    for tag in add_tags:
        if tag and tag not in current_tags:
            path_parts = add(tag, path_parts)

    # reposition the file in the tree, favoring tags
    # in the form of directory names
    if use_dirs:
        path_parts = resolve_dirs(path_parts)

    return f_join(path_parts)


def run(add_tags, remove_tags, files):
    for f in files:
        print(f)
        print(run_file(add_tags, remove_tags, f))


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
                files.add(os.path.abspath(option))
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
