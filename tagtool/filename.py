
import re
import os
from .config import Config


class Filename:
    """ Class for manipulating filenames in a tag-based fashion """

    def __init__(self, filestr, config={}):
        # ensure that paths are always absolute
        filestr = os.path.abspath(filestr)

        # save a copy of the original path
        self.filestr = filestr

        # split out the dirs, the filename, and the extension
        self.dirs, filestr  = os.path.split(filestr)
        self.name, self.ext = os.path.splitext(filestr)

        # load the config for this file
        # considers .tagdir rules, and then any overrides given in "config"
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

        tags.update(self._raw_get_tags(self.name))

        if self.config["use_dirs"]:
            tags.update(self._raw_get_tags(self.dirs))

        return tags


    def has_tag(self, tag):
        if self._raw_has_tag(self.name, tag):
            return True

        if self.config["use_dirs"]:
            if self._raw_has_tag(self.dirs, tag):
                return True

        return False


    def add_remove_tags(self, add_tags, remove_tags):
        # remove the requested tags
        for tag in remove_tags:
            self._remove(tag)

        # add the requested tags
        for tag in add_tags:
            self._add(tag)

        # reposition the file in the tree, favoring tags
        # in the form of directory names
        if self.config["use_dirs"]:
            self._resolve_dirs()

        if self.name == "":
            self.name = self.config["no_tags_filename"]


    # def valid_tag(tag, config):
    #     if tag == "":
    #         return False
    #     return re.search(config["tag_delims"], tag) == None


    # searches for a tag in an arbitrary string
    def _raw_has_tag(self, s, tag):

        flags = 0 if self.config["case_sensitive"] else re.IGNORECASE

        #           (^|[ .,_-])tag($|[ .,_-])
        pattern  = "(^|" + self.config["tag_delims"] + ")" + \
                    tag + \
                    "($|" + self.config["tag_delims"] + ")"
        return re.search(pattern, s, flags) != None


    # returns the tagset for an arbitrary string
    def _raw_get_tags(self, s):
        tags = set(re.split(self.config["tag_delims"], s))

        if not self.config["case_sensitive"]:
            tags = set([x.lower() for x in tags])

        return set(filter(bool, tags)) # strain out empty strings


    def _add(self, tag):
        """ adds a tag to this file """
        # if there is a dir to encode this tag, it will be removed from
        # the filename in the resolve_dirs() function

        # if the tag is already there, do nothing
        if self.has_tag(tag):
            return

        if self.name != "":
            tag += self.config["default_delim"]

        self.name = tag + self.name


    def _remove(self, tag):
        """ remove tags from the file """

        flags = 0 if self.config["case_sensitive"] else re.IGNORECASE

        if not self.config["case_sensitive"]:
            tag = tag.lower()

        # Hard to combine these into one regex because python complains about not
        # having fixed a length look-behind. Look-behind is necessary to prevent
        # the leading delimeter from being eaten.

        # WARNING: the order here is important. Deleting tags from the front or the
        # back will cause inner tags to become front or back tags. This causes
        # problems if there are two of the same tag adjacent to one-another.
        mid_pattern   = ("(?<=%s)" % self.config["tag_delims"]) + \
                        tag + \
                        self.config["tag_delims"]

        #                (^|[ .,_-])tag($|[ .,_-])
        edge_pattern  = "(^|" + self.config["tag_delims"] + ")" + \
                        tag + \
                        "($|" + self.config["tag_delims"] + ")"

        # erase any tag instances from the name
        self.name = re.sub(mid_pattern, "", self.name, flags=flags)
        self.name = re.sub(edge_pattern, "", self.name, flags=flags)

        # remove tags from the dirs
        if self.config["use_dirs"]:
            self.dirs = re.sub(mid_pattern, "", self.dirs, flags=flags)
            self.dirs = re.sub(edge_pattern, "", self.dirs, flags=flags)



    # Only used if self.config["use_dirs"] == True
    # Sinks a file back down the directory tree, according to its tags
    # Directories are favored as tag storage. Also handles deletion of tags
    # from dir names carrying multiple tags
    def _resolve_dirs(self):
        tags = self.get_tags()

        # recurse to find the best directory path for this tagset
        path, remaining_tags = self._find_best_path(self.config.root_dir, tags)

        # find out which tags were handled by directories
        # and remove them from the filename
        for tag in tags.difference(remaining_tags):
            self._remove(tag)

        # do this AFTER, since self._remove() will removed tags from the dirs
        self.dirs = os.path.relpath(path, self.config.root_dir)

        # ensure that any remaining tags are encoded in the filename
        # this handles cases where directories contain multiple tags
        # self._add() will skip tags that are already present
        for tag in remaining_tags:
            self._add(tag)


    # recursive function that determines the filepath that encodes the most
    # of the given tagset.
    def _find_best_path(self, path, tags):

        best_path = path
        best_tags_left = set(tags) # goal is to minimize len() for this

        # search all of the directories at the current path
        for d in dirs_at(os.path.join(self.config.root_dir, path)):

            d_tags = self._raw_get_tags(d)

            # if the tags of the directory name are all tags that we're looking for
            if all([t in tags for t in d_tags]):
                # we've found a valid dir to put the file in
                
                # prepare to recurse by removing the tags consumed by this dir name
                next_tags = set(tags).difference(d_tags)

                # recurse
                r = self._find_best_path(os.path.join(path, d), next_tags)

                # check to see if a better score was achieved
                if(len(r[1]) < len(best_tags_left)):
                    best_path      = r[0]
                    best_tags_left = r[1]

            # skip directories that contain tags we AREN'T looking for 

        return (best_path, best_tags_left)
