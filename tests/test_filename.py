#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from tagtool import Filename, get_config

# a default Filename object for testing with
f = Filename("tree/a/a_b_c")

# make sure that the config found the .tagdir
assert(f.config["root_dir"]         == os.path.abspath("tree/"))
assert(f.config["use_dirs"]         == True)
assert(f.config["default_delim"]    == "_")
assert(f.config["no_tags_filename"] == "unknown")
assert(f.config["case_sensitive"]   == True)

"""
tree/
├── a/
│   ├── a_b_c
│   ├── b/
│   │   └── .gitkeep
│   └── c/
│       └── .gitkeep
├── d/
│   └── a/
│       └── .gitkeep
├── f_g/
│   └── a_b
└── .tagdir
"""



"""
Utils
"""

def try_add_remove(f, add_tags, remove_tags, overrides):
    # make a new file object
    filename = Filename(f, overrides)
    # run the tagger
    filename.add_remove_tags(add_tags, remove_tags)
    # return a concise path
    return os.path.relpath(str(filename), "./")


def try_find_best_path(tags):
    # start the path finder at the root dir
    r = f._find_best_path(f.config["root_dir"], tags)
    # return a concise path
    return (os.path.relpath(r[0], "./"), r[1])



"""
Private Filename functions
"""

def test_find_best_path():

    # simple finding of directories
    assert( try_find_best_path(["a"])      == ("tree/a",   set()) )
    assert( try_find_best_path(["a", "b"]) == ("tree/a/b", set()) )
    assert( try_find_best_path(["a", "d"]) == ("tree/d/a", set()) )

    # non-existant directories
    assert( try_find_best_path(["b"])      == ("tree",   {"b"}) )
    assert( try_find_best_path(["b", "c"]) == ("tree",   {"b", "c"}) )

    # combinations of the above
    assert( try_find_best_path(["b", "d"]) == ("tree/d",   {"b"}) )

    # the ambiguous case
    # currently an arbitrary decision, and may vary from platform to platform
    r = try_find_best_path(["a", "b", "c"])
    assert( r == ("tree/a/b", {"c"}) \
            or \
            r == ("tree/a/c", {"b"}) )


def test_raw_get_tags():

    assert( f._raw_get_tags("a")       == {"a"} )
    assert( f._raw_get_tags("ab")      == {"ab"} )
    assert( f._raw_get_tags("a_b")     == {"a", "b"} )
    assert( f._raw_get_tags("ab_cd")   == {"ab", "cd"} )
    assert( f._raw_get_tags("a_b_c_d") == {"a", "b", "c", "d"} )
    assert( f._raw_get_tags("a_a_a_d") == {"a", "d"} )


def test_raw_has_tag():

    assert(     f._raw_has_tag("a", "a") )
    assert(     f._raw_has_tag("a_a", "a") )
    assert(     f._raw_has_tag("a_b", "a") )
    assert(     f._raw_has_tag("a_b", "b") )
    assert(     f._raw_has_tag("_a_b_", "a") )
    assert(     f._raw_has_tag("_a_b_", "b") )
    assert( not f._raw_has_tag("a_b", "c") )


"""
Tagging Logic
"""

def test_tag_add_name():

    # DON'T use directories
    overrides = { "use_dirs": False }

    # don't add tags that are already present
    assert( try_add_remove("tree/a/a_b_c", ["a"], [], overrides) == "tree/a/a_b_c" )

    # add tags
    assert( try_add_remove("tree/a/a_b_c", ["z"], [], overrides) == "tree/a/z_a_b_c" )

    # combination of the two above
    assert( try_add_remove("tree/a/a_b_c", ["z", "a"], [], overrides) == "tree/a/z_a_b_c" )

    # add multiple tags
    assert( try_add_remove("tree/a/a_b_c", ["x", "y", "z"], [], overrides) == "tree/a/z_y_x_a_b_c" )


def test_tag_remove_name():
    # DON'T use directories
    overrides = { "use_dirs": False }

    # remove tags from front of name
    assert( try_add_remove("tree/a/a_b_c", [], ["a"], overrides) == "tree/a/b_c" )

    # remove tags from middle of name
    assert( try_add_remove("tree/a/a_b_c", [], ["b"], overrides) == "tree/a/a_c" )

    # remove tags from end of name
    assert( try_add_remove("tree/a/a_b_c", [], ["c"], overrides) == "tree/a/a_b" )

    # remove multiple tags
    assert( try_add_remove("tree/a/a_b_c", [], ["a", "b"], overrides) == "tree/a/c" )

    # remove multiple tags
    assert( try_add_remove("tree/a/a_b_c", [], ["b", "c"], overrides) == "tree/a/a" )

    # remove all tags
    assert( try_add_remove("tree/a/a_b_c", [], ["a", "b", "c"], overrides) == "tree/a/" + f.config["no_tags_filename"] )



def test_tag_add_dirs():
    # USE directories
    overrides = { "use_dirs": True }

    # don't add tags that are already present, and recompute dirs
    # also an ambiguous case (see note in test_dir_computer)
    r = try_add_remove("tree/a/a_b_c", ["a"], [], overrides)
    assert( r == "tree/a/b/c" \
            or \
            r == "tree/a/c/b" )

    # don't move to a new directory unless ALL tags match
    r = try_add_remove("tree/a/a_b_c", ["f"], [], overrides)
    assert( r == "tree/a/b/f_c" \
            or \
            r == "tree/a/c/f_b")


def test_tag_remove_dirs():
    # USE directories
    overrides = { "use_dirs": True }

    # general tag removal
    assert( try_add_remove("tree/a/a_b_c", [], ["a"], overrides)      == "tree/b_c" )
    assert( try_add_remove("tree/f_g/a_b", [], ["a"], overrides)      == "tree/f_g/b" )
    assert( try_add_remove("tree/f_g/a_b", [], ["f", "g"], overrides) == "tree/a/b/" + f.config["no_tags_filename"] )

    # tag removal causing tags in name to be used in dirs
    assert( try_add_remove("tree/a/a_b_c",   [], ["c"], overrides)    == "tree/a/b/" + f.config["no_tags_filename"] )

    # tag removal from multi-tag directories
    assert( try_add_remove("tree/f_g/a_b", [], ["f"], overrides)      == "tree/a/b/g" )
    assert( try_add_remove("tree/f_g/a_b", [], ["g"], overrides)      == "tree/a/b/f" )
    assert( try_add_remove("tree/f_g/a_b", [], ["f", "a"], overrides) == "tree/g_b" )
    assert( try_add_remove("tree/f_g/a_b", [], ["f", "b"], overrides) == "tree/a/g" )
