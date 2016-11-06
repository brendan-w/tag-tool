
import re
import os
import configparser

from .utils import *



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

DEFAULT_CONFIG = {
    "root_dir"         : "", # the directory containing the .tagdir file
    "use_dirs"         : False,
    "tag_delims"       : " ,_&=.-+()[]{}/\\",
    "default_delim"    : "_",
    "no_tags_filename" : "unknown",
    "case_sensitive"   : True
}


def get_config(path="", overrides={}):
    config = DEFAULT_CONFIG.copy()

    # pick a root directory
    # if no path is specified, use the CWD
    # if no .tagdir is found, use the CWD
    if not path:
        path = os.path.abspath(".")

    config["root_dir"] = find_above(path, TAGDIR_FILENAME)

    if not config["root_dir"]:
        config["root_dir"] = os.path.abspath(".")


    if config["root_dir"] != "":
        # load the config

        parser = configparser.SafeConfigParser()
        parser.read(os.path.join(config["root_dir"], TAGDIR_FILENAME))

        if TAGDIR_SECTION in parser:
            c = parser[TAGDIR_SECTION]

            config["use_dirs"]         = c.getboolean("use_dirs",       True)
            config["tag_delims"]       = c.get("tag_delims",            config["tag_delims"])
            config["default_delim"]    = c.get("default_delim",         config["default_delim"])
            config["no_tags_filename"] = c.get("no_tags_filename",      config["no_tags_filename"])
            config["case_sensitive"]   = c.getboolean("case_sensitive", config["case_sensitive"])

    # process any commandline overrides we were given
    config.update(overrides)

    # post process

    # make tag_delims an actual regex
    config["tag_delims"] = "[" + re.escape(config["tag_delims"]) + "]"

    return config
