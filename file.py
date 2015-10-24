
import os
from utils import *

"""
Main File Class
"""


class File:
    def __init__(self, filestr):
        # ensure that paths are always absolute
        filestr = os.path.abspath(filestr)

        # save a copy of the original path
        self.filestr = filestr

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

        path = os.path.join(path, filename)

        # normalize the path (for when self.dirs == "./")
        return os.path.normpath(path)


    def get_tags(self):
        """ returns a set of tags on this file """

        tags = set()

        tags.update(get_tags(self.name))

        if settings.use_dirs:
            tags.update(get_tags(self.dirs))

        return tags


    def has_tag(self, tag):
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

        # do this AFTER, since self.__remove() will removed tags from the dirs
        self.dirs = os.path.relpath(path, settings.root_dir)

        # ensure that any remaining tags are encoded in the filename
        # this handles cases where directories contain multiple tags
        # self.__add() will skip tags that are already present
        for tag in remaining_tags:
            self.__add(tag)