#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from tagtool import Filename, get_config

# move into our testing directory
os.chdir("tree/")
root_dir = os.path.abspath(os.getcwd())

# a default Filename object for testing with
f = Filename("a/a_b_c")

# make sure that the config found the .tagdir
assert(f.config["root_dir"]         == root_dir)
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

def try_add_remove(config, f, add_tags, remove_tags):
    f = File(os.path.join(cwd, f), config)
    f.add_remove_tags(add_tags, remove_tags)
    return os.path.relpath(str(f), cwd)



"""
Private Filename functions
"""

def test_find_best_path():

    # simple finding of directories
    assert( f._find_best_path("./", ["a"])      == ("./a",   set()) )
    assert( f._find_best_path("./", ["a", "b"]) == ("./a/b", set()) )
    assert( f._find_best_path("./", ["a", "d"]) == ("./d/a", set()) )

    # non-existant directories
    assert( f._find_best_path("./", ["b"])      == ("./",   {"b"}) )
    assert( f._find_best_path("./", ["b", "c"]) == ("./",   {"b", "c"}) )

    # combinations of the above
    assert( f._find_best_path("./", ["b", "d"]) == ("./d",   {"b"}) )

    # the ambiguous case
    # currently an arbitrary decision, and may vary from platform to platform
    r = f._find_best_path("./", ["a", "b", "c"])
    assert( r == ("./a/b", {"c"}) \
            or \
            r == ("./a/c", {"b"}) )


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


# def test_tag_add_name():
#     # DON'T use directories
#     config = { "use_dirs": False }

#     # don't add tags that are already present
#     assert( try_add_remove(config, "a/a_b_c", ["a"], []) == "a/a_b_c" )

#     # add tags
#     assert( try_add_remove(config, "a/a_b_c", ["z"], []) == "a/z_a_b_c" )

#     # combination of the two above
#     assert( try_add_remove(config, "a/a_b_c", ["z", "a"], []) == "a/z_a_b_c" )

#     # add multiple tags
#     assert( try_add_remove(config, "a/a_b_c", ["x", "y", "z"], []) == "a/z_y_x_a_b_c" )


# def test_tag_remove_name():
#     # DON'T use directories
#     config = { "use_dirs": False }

#     # remove tags from front of name
#     assert( try_add_remove(config, "a/a_b_c", [], ["a"]) == "a/b_c" )

#     # remove tags from middle of name
#     assert( try_add_remove(config, "a/a_b_c", [], ["b"]) == "a/a_c" )

#     # remove tags from end of name
#     assert( try_add_remove(config, "a/a_b_c", [], ["c"]) == "a/a_b" )

#     # remove multiple tags
#     assert( try_add_remove(config, "a/a_b_c", [], ["a", "b"]) == "a/c" )

#     # remove multiple tags
#     assert( try_add_remove(config, "a/a_b_c", [], ["b", "c"]) == "a/a" )

#     # remove all tags
#     assert( try_add_remove(config, "a/a_b_c", [], ["a", "b", "c"]) == "a/" + default_config["no_tags_filename"] )



# def test_tag_add_dirs():
#     # USE directories
#     config = { "use_dirs": True }

#     # don't add tags that are already present, and recompute dirs
#     # also an ambiguous case (see note in test_dir_computer)
#     r = try_add_remove(config, "a/a_b_c", ["a"], [])
#     assert( r == "a/b/c" \
#             or \
#             r == "a/c/b" )

#     # don't move to a new directory unless ALL tags match
#     r = try_add_remove(config, "a/a_b_c", ["f"], [])
#     assert( r == "a/b/f_c" \
#             or \
#             r == "a/c/f_b")


# def test_tag_remove_dirs():
#     # USE directories
#     config = { "use_dirs": True }

#     # general tag removal
#     assert( try_add_remove(config, "a/a_b_c", [], ["a"])      == "b_c" )
#     assert( try_add_remove(config, "f_g/a_b", [], ["a"])      == "f_g/b" )
#     assert( try_add_remove(config, "f_g/a_b", [], ["f", "g"]) == "a/b/" + default_config["no_tags_filename"] )

#     # tag removal causing tags in name to be used in dirs
#     assert( try_add_remove(config, "a/a_b_c",   [], ["c"])    == "a/b/" + default_config["no_tags_filename"] )

#     # tag removal from multi-tag directories
#     assert( try_add_remove(config, "f_g/a_b", [], ["f"])      == "a/b/g" )
#     assert( try_add_remove(config, "f_g/a_b", [], ["g"])      == "a/b/f" )
#     assert( try_add_remove(config, "f_g/a_b", [], ["f", "a"]) == "g_b" )
#     assert( try_add_remove(config, "f_g/a_b", [], ["f", "b"]) == "a/g" )
