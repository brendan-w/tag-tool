
import re
import os
import configparser


"""
Settings
"""

# the name of the settings file that specifies the scope of directory tagging
tagdir_filename = ".tagdir"

# the main settings object with default settings
# (defaults are used for when no .tagdir file is found)
class Settings:

    root_dir         = ""
    use_dirs         = False
    tag_delims       = "[ ,_&=%%\\.\\-\\+\\(\\)\\[\\]\\{\\}\\/\\\\]"
    default_delim    = "_"
    no_tags_filename = "unknown"
    find_cmd         = "find %s -type f %s ! -path */.* ! -perm -o=x";
    case_sensitive   = True
    verbose          = False

    def __init__(self):
        self.root_dir = find_above(os.getcwd(), tagdir_filename)
        self.use_dirs = (self.root_dir != "") # could eventually be disabled by an option
        if self.root_dir == "":
            self.root_dir = os.getcwd()


"""
General Utils
"""


# recursive function that determines the filepath that encodes the most
# of the given tagset.
def find_best_path(path, tags):

    best_path = path
    best_tags_left = set(tags) # goal is to minimize len() for this

    # search all of the directories at the current path
    for d in dirs_at(os.path.join(settings.root_dir, path)):

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


def has_tag(s, tag):

    flags = 0 if settings.case_sensitive else re.IGNORECASE

    #           (^|[ .,_-])tag($|[ .,_-])
    pattern  = "(^|" + settings.tag_delims + ")" + tag + "($|" + settings.tag_delims + ")"
    return re.search(pattern, s, flags) != None


# returns the tagset for an arbitrary string
def get_tags(s):
    tags = set(re.split(settings.tag_delims, s))

    if not settings.case_sensitive:
        tags = set([x.lower() for x in tags])

    return set(filter(bool, tags)) # strain out empty strings


def valid_tag(tag):
    if tag == "":
        return False
    return re.search(settings.tag_delims, tag) == None




# import this object for settings
settings = Settings()
