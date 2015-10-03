
import re
import os
from collections import namedtuple



"""
Settings
"""


# the name of the settings file that specifies the scope of directory tagging
tagdir_filename = ".tagdir"

# the main settings object with default settings
# (defaults are used for when no .tagdir file is found)
class settings:
    verbose          = False
    root_dir         = ""
    use_name         = True
    use_dirs         = False
    tag_delims       = "[ ,_&=%%\\/\\.\\-\\+\\(\\)\\[\\]\\{\\}]"
    default_delim    = "_"
    no_tags_filename = "unknown"
    find_cmd         = "find . -type f %s ! -path */.* ! -perm -o=x";
    case_sensitive   = True


def load_settings():
    settings.root_dir = find_above(os.getcwd(), tagdir_filename)
    settings.use_dirs = (settings.root_dir != "") # could eventually be disabled by an option


# recursively finds the nearest .tagdir file denoting the limit for moving files
def find_above(path, filename):
    if os.path.isfile(os.path.join(path, filename)):
        return path
    else:
        if path == "/":
            return ""
        else:
            return find_above(os.path.dirname(path), filename)


"""
General Utils
"""


PathParts = namedtuple('PathParts', 'dirs name ext')


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
    if settings.use_dirs:
        dirs = os.path.relpath(dirs, settings.root_dir)

    return PathParts(dirs, name, ext)


# reassemble a PathParts struct back into a filename
def f_join(path_parts):
    path = path_parts.dirs
    filename = path_parts.name + path_parts.ext

    # if a root dir was used, resolve the reference
    if settings.use_dirs:
        path = os.path.join(settings.root_dir, path)

    return os.path.join(path, filename)


# returns the tagset for an arbitrary string
def get_tags(s):
    tags = set(re.split(settings.tag_delims, s))

    if not settings.case_sensitive:
        tags = set([x.lower() for x in tags])

    return set(filter(bool, tags)) # strain out empty strings


# returns a set of tags on this file
def get_all_tags(path_parts):

    tags = set()

    if settings.use_name:
        tags.update(get_tags(path_parts.name))

    if settings.use_dirs:
        tags.update(get_tags(path_parts.dirs))

    return tags
