#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from tagtool import Filename, get_config

# move into our testing directory
os.chdir("tree/")

default_file = "a/a_b_c"
default_config = get_config("./")

# make sure that the config found the .tagdir
assert(default_config["root_dir"]         == "./")
assert(default_config["use_dirs"]         == True)
assert(default_config["default_delim"]    == "_")
assert(default_config["no_tags_filename"] == "unknown")
assert(default_config["case_sensitive"]   == True)

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


def try_find_best_path(tags):
    r = find_best_path(cwd, set(tags), default_config)
    return (os.path.relpath(r[0], cwd), r[1])


def test_find_best_path():

    f = Filename(default_file)

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


# def test_core_valid_tag():
#     assert(     valid_tag("a", default_config) )
#     assert(     valid_tag("abcdefg", default_config) )
#     assert( not valid_tag("", default_config) )
#     assert( not valid_tag("_a", default_config) )
#     assert( not valid_tag("a_", default_config) )
#     assert( not valid_tag("a_b", default_config) )


# def test_core_get_tags():
#     assert( get_tags("a", default_config)   == {"a"} )
#     assert( get_tags("ab", default_config)  == {"ab"} )
#     assert( get_tags("a_b", default_config) == {"a", "b"} )
#     assert( get_tags("ab_cd", default_config) == {"ab", "cd"} )
#     assert( get_tags("a_b_c_d", default_config) == {"a", "b", "c", "d"} )
#     assert( get_tags("a_a_a_d", default_config) == {"a", "d"} )


# def test_core_has_tag():
#     assert(     has_tag("a", "a", default_config) )
#     assert(     has_tag("a_a", "a", default_config) )
#     assert(     has_tag("a_b", "a", default_config) )
#     assert(     has_tag("a_b", "b", default_config) )
#     assert(     has_tag("_a_b_", "a", default_config) )
#     assert(     has_tag("_a_b_", "b", default_config) )
#     assert( not has_tag("a_b", "c", default_config) )


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
