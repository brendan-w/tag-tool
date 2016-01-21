
import re
import os
import configparser



"""
Constants
"""

# the name of the settings file that specifies the scope of directory tagging
TAGDIR_FILENAME = ".tagdir"

# the config section containing settings
TAGDIR_SECTION = "tagdir"


"""
General Utils
"""

# recursive function that determines the filepath that encodes the most
# of the given tagset.
def find_best_path(path, tags, config):

    best_path = path
    best_tags_left = set(tags) # goal is to minimize len() for this

    # search all of the directories at the current path
    for d in dirs_at(os.path.join(config.root_dir, path)):

        d_tags = get_tags(d, config)

        # if the tags of the directory name are all tags that we're looking for
        if all([t in tags for t in d_tags]):
            # we've found a valid dir to put the file in
            
            # prepare to recurse by removing the tags consumed by this dir name
            next_tags = set(tags).difference(d_tags)

            # recurse
            r = find_best_path(os.path.join(path, d), next_tags, config)

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
        if not path or path == "/":
            return ""
        else:
            return find_above(os.path.dirname(path), filename)


# lists only directories at the given path
def dirs_at(path):
    return [ name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name)) ]


# searches for a tag in an arbitrary string
def has_tag(s, tag, config):

    flags = 0 if config["case_sensitive"] else re.IGNORECASE

    #           (^|[ .,_-])tag($|[ .,_-])
    pattern  = "(^|" + config["tag_delims"] + ")" + tag + "($|" + config["tag_delims"] + ")"
    return re.search(pattern, s, flags) != None


# returns the tagset for an arbitrary string
def get_tags(s, config):
    tags = set(re.split(config["tag_delims"], s))

    if not config["case_sensitive"]:
        tags = set([x.lower() for x in tags])

    return set(filter(bool, tags)) # strain out empty strings


def valid_tag(tag, config):
    if tag == "":
        return False
    return re.search(config["tag_delims"], tag) == None




"""
Settings
"""

# the main settings object with default settings
# (defaults are used for when no .tagdir file is found)
class Config:


    # the root directory for tag operations with dirs
    # should only be used when settings.use_dirs == True
    root_dir = ""

    # default settings
    attrs = {
        "use_dirs"         : False,
        "tag_delims"       : " ,_&=.-+()[]{}/\\",
        "default_delim"    : "_",
        "no_tags_filename" : "unknown",
        "find_cmd"         : "find {dir} -type f {pattern} ! -path */.* ! -perm -o=x",
        "case_sensitive"   : True,
        "verbose"          : False
    }


    def __init__(self, path="", overrides={}):

        self.root_dir = find_above(path, TAGDIR_FILENAME)
        self.attrs["use_dirs"] = (self.root_dir != "") # could eventually be disabled by an option

        # if we found a .tagdir file, read it
        if self.root_dir != "":
            tagdir_file = os.path.join(self.root_dir, TAGDIR_FILENAME)
            self._load_config(tagdir_file)

        # override with command line options
        self._override(overrides)

        # turn tag_delims into a regex
        self.attrs["tag_delims"] = "[" + re.escape(self.attrs["tag_delims"]) + "]"


    def __getitem__(self, key):
        return self.attrs.get(key, None)


    def _override(self, overrides):
        for key in overrides:
            self.attrs[key] = overrides[key]


    def _load_config(self, config_file):
        config = configparser.SafeConfigParser()
        config.read(config_file)

        if TAGDIR_SECTION in config:
            for key in self.attrs:
                if key in config[TAGDIR_SECTION]:
                    self.attrs[key] = config[TAGDIR_SECTION][key]
                    print("found key: %s" % key)


    def write_config(self, file_name):
        pass




"""
Main File Class
"""

class File:
    def __init__(self, filestr, config={}):
        # ensure that paths are always absolute
        filestr = os.path.abspath(filestr)

        # save a copy of the original path
        self.filestr = filestr

        # split out the dirs, the filename, and the extension
        self.dirs, filestr  = os.path.split(filestr)
        self.name, self.ext = os.path.splitext(filestr)

        self.config = Config(self.dirs, config)

        # if dirs are being used, do NOT consider the path
        # to the root tag directory
        if self.config["use_dirs"]:
            self.dirs = os.path.relpath(self.dirs, self.config.root_dir)


    def __str__(self):
        path = self.dirs
        filename = self.name + self.ext

        # if a root dir was used, resolve the reference
        if self.config["use_dirs"]:
            path = os.path.join(self.config.root_dir, path)

        path = os.path.join(path, filename)

        # normalize the path (for when self.dirs == "./")
        return os.path.normpath(path)


    def get_tags(self):
        """ returns a set of tags on this file """

        tags = set()

        tags.update(get_tags(self.name, self.config))

        if self.config["use_dirs"]:
            tags.update(get_tags(self.dirs, self.config))

        return tags


    def has_tag(self, tag):
        if has_tag(self.name, tag, self.config):
            return True

        if self.config["use_dirs"]:
            if has_tag(self.dirs, tag, self.config):
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
        if self.config["use_dirs"]:
            self.__resolve_dirs()

        if self.name == "":
            self.name = self.config["no_tags_filename"]


    def __add(self, tag):
        # adds a tag to this file's name
        # if there is a dir to encode this tag, it will be removed from
        # the filename in the resolve_dirs() function

        # if the tag is already there, do nothing
        if self.has_tag(tag):
            return

        if self.name != "":
            tag += self.config["default_delim"]

        self.name = tag + self.name


    def __remove(self, tag):
        """ remove tags from the name """

        # Hard to combine these into one regex because python complains about not
        # having fixed a length look-behind. Look-behind is necessary to prevent
        # the leading delimeter from being eaten.

        # WARNING: the order here is important. Deleting tags from the front or the
        # back will cause inner tags to become front or back tags. This causes
        # problems if there are two of the same tag adjacent to one-another.
        mid_pattern   = ("(?<=%s)" % self.config["tag_delims"]) + tag + self.config["tag_delims"]

        #                (^|[ .,_-])tag($|[ .,_-])
        edge_pattern  = "(^|" + self.config["tag_delims"] + ")" + tag + "($|" + self.config["tag_delims"] + ")"

        # erase any tag instances from the name
        self.name = re.sub(mid_pattern, "", self.name)
        self.name = re.sub(edge_pattern, "", self.name)

        # remove tags from the dirs
        if self.config["use_dirs"]:
            self.dirs = re.sub(mid_pattern, "", self.dirs)
            self.dirs = re.sub(edge_pattern, "", self.dirs)



    # Only used if self.config["use_dirs"] == True
    # Sinks a file back down the directory tree, according to its tags
    # Directories are favored as tag storage. Also handles deletion of tags
    # from dir names carrying multiple tags
    def __resolve_dirs(self):
        tags = self.get_tags()

        # recurse to find the best directory path for this tagset
        path, remaining_tags = find_best_path(self.config.root_dir, tags, self.config)

        # find out which tags were handled by directories
        # and remove them from the filename
        for tag in tags.difference(remaining_tags):
            self.__remove(tag)

        # do this AFTER, since self.__remove() will removed tags from the dirs
        self.dirs = os.path.relpath(path, self.config.root_dir)

        # ensure that any remaining tags are encoded in the filename
        # this handles cases where directories contain multiple tags
        # self.__add() will skip tags that are already present
        for tag in remaining_tags:
            self.__add(tag)
