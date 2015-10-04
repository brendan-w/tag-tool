
import re
import os



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
    tag_delims       = "[ ,_&=%%\\/\\.\\-\\+\\(\\)\\[\\]\\{\\}\\\\]"
    default_delim    = "_"
    no_tags_filename = "unknown"
    find_cmd         = "find %s -type f %s ! -path */.* ! -perm -o=x";
    case_sensitive   = True


def load_settings():
    settings.root_dir = find_above(os.getcwd(), tagdir_filename)
    settings.use_dirs = (settings.root_dir != "") # could eventually be disabled by an option
    if settings.root_dir == "":
        settings.root_dir = "."


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


class File:
    def __init__(self, filestr):
        # split out the dirs, the filename, and the extension
        self.dirs, filestr  = os.path.split(filestr)
        self.name, self.ext = os.path.splitext(filestr)

        # if dirs are being used, do NOT consider the path
        # to the root tag directory
        if settings.use_dirs:
            self.dirs = os.path.relpath(self.dirs, settings.root_dir)


    def __str__(self):
        path = self.dirs
        filename = self.name + self.ext

        # if a root dir was used, resolve the reference
        if settings.use_dirs:
            path = os.path.join(settings.root_dir, path)

        return os.path.join(path, filename)


    def get_tags(self):
        """ returns a set of tags on this file """

        tags = set()

        if settings.use_name:
            tags.update(get_tags(self.name))

        if settings.use_dirs:
            tags.update(get_tags(self.dirs))

        return tags


    def has_tag(self, tag):
        if settings.use_name:
            if has_tag(self.name, tag):
                return True

        if settings.use_dirs:
            if has_tag(self.dirs, tag):
                return True

        return False


    def add_remove_tags(self, add_tags, remove_tags):
        # remove the requested tags
        for tag in remove_tags:
            self.__remove(tag)

        # add the requested tags
        for tag in add_tags:
            self.__add(tag)

        # reposition the file in the tree, favoring tags
        # in the form of directory names
        if settings.use_dirs:
            self.__resolve_dirs()

        if self.name == "":
            self.name = settings.no_tags_filename


    def __add(self, tag):
        # adds a tag to this file's name
        # if there is a dir to encode this tag, it will be removed from
        # the filename in the resolve_dirs() function

        # if the tag is already there, do nothing
        if self.has_tag(tag):
            return

        if self.name != "":
            tag += settings.default_delim

        self.name = tag + self.name


    def __remove(self, tag):
        """ remove tags from the name """

        # Hard to combine these into one regex because python complains about not
        # having fixed a length look-behind. Look-behind is necessary to prevent
        # the leading delimeter from being eaten.

        # WARNING: the order here is important. Deleting tags from the front or the
        # back will cause inner tags to become front or back tags. This causes
        # problems if there are two of the same tag adjacent to one-another.
        mid_pattern   = ("(?<=%s)" % settings.tag_delims) + tag + settings.tag_delims

        #                (^|[ .,_-])tag($|[ .,_-])
        edge_pattern  = "(^|" + settings.tag_delims + ")" + tag + "($|" + settings.tag_delims + ")"

        # erase any tag instances from the name
        if settings.use_name:
            self.name = re.sub(mid_pattern, "", self.name)
            self.name = re.sub(edge_pattern, "", self.name)

        # remove tags from the dirs
        if settings.use_dirs:
            self.dirs = re.sub(mid_pattern, "", self.dirs)
            self.dirs = re.sub(edge_pattern, "", self.dirs)



    # Only used if settings.use_dirs == True
    # Sinks a file back down the directory tree, according to its tags
    # Directories are favored as tag storage. Also handles deletion of tags
    # from dir names carrying multiple tags
    def __resolve_dirs(self):
        tags = self.get_tags()


        # recurse to find the best directory path for this tagset
        path, remaining_tags = find_best_path(settings.root_dir, tags)

        # find out which tags were handled by directories
        # and remove them from the filename
        for tag in tags.difference(remaining_tags):
            self.__remove(tag)

        if settings.use_dirs:
            self.dirs = os.path.relpath(path, settings.root_dir)





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
    return re.search(settings.tag_delims, tag) == None
