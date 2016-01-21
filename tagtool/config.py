
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

        # turn tag_delims into a regex class
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
