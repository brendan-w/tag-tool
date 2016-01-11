#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

# move into our test_tree directory
os.chdir("test_tree")
cwd = os.getcwd()

from core import *


"""
test_tree/
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

def try_add_remove(f, add_tags, remove_tags):
    f = File(os.path.join(cwd, f))
    f.add_remove_tags(add_tags, remove_tags)
    return os.path.relpath(str(f), cwd)


def try_find_best_path(tags):
    r = find_best_path(cwd, set(tags))
    return (os.path.relpath(r[0], cwd), r[1])


def test_core_valid_tag():
    assert(     valid_tag("a") )
    assert(     valid_tag("abcdefg") )
    assert( not valid_tag("") )
    assert( not valid_tag("_a") )
    assert( not valid_tag("a_") )
    assert( not valid_tag("a_b") )


def test_core_get_tags():
    assert( get_tags("a")   == {"a"} )
    assert( get_tags("ab")  == {"ab"} )
    assert( get_tags("a_b") == {"a", "b"} )
    assert( get_tags("ab_cd") == {"ab", "cd"} )
    assert( get_tags("a_b_c_d") == {"a", "b", "c", "d"} )
    assert( get_tags("a_a_a_d") == {"a", "d"} )


def test_core_has_tag():
    assert(     has_tag("a", "a") )
    assert(     has_tag("a_a", "a") )
    assert(     has_tag("a_b", "a") )
    assert(     has_tag("a_b", "b") )
    assert(     has_tag("_a_b_", "a") )
    assert(     has_tag("_a_b_", "b") )
    assert( not has_tag("a_b", "c") )


def test_tag_add_name():
    # DON'T use directories
    settings.use_dirs = False

    # don't add tags that are already present
    assert( try_add_remove("a/a_b_c", ["a"], []) == "a/a_b_c" )

    # add tags
    assert( try_add_remove("a/a_b_c", ["z"], []) == "a/z_a_b_c" )

    # combination of the two above
    assert( try_add_remove("a/a_b_c", ["z", "a"], []) == "a/z_a_b_c" )

    # add multiple tags
    assert( try_add_remove("a/a_b_c", ["x", "y", "z"], []) == "a/z_y_x_a_b_c" )


def test_tag_remove_name():
    # DON'T use directories
    settings.use_dirs = False

    # remove tags from front of name
    assert( try_add_remove("a/a_b_c", [], ["a"]) == "a/b_c" )

    # remove tags from middle of name
    assert( try_add_remove("a/a_b_c", [], ["b"]) == "a/a_c" )

    # remove tags from end of name
    assert( try_add_remove("a/a_b_c", [], ["c"]) == "a/a_b" )

    # remove multiple tags
    assert( try_add_remove("a/a_b_c", [], ["a", "b"]) == "a/c" )

    # remove multiple tags
    assert( try_add_remove("a/a_b_c", [], ["b", "c"]) == "a/a" )

    # remove all tags
    assert( try_add_remove("a/a_b_c", [], ["a", "b", "c"]) == "a/" + settings.no_tags_filename )



def test_dir_computer():

    # simple finding of directories
    assert( try_find_best_path(["a"])      == ("a",   set()) )
    assert( try_find_best_path(["a", "b"]) == ("a/b", set()) )
    assert( try_find_best_path(["a", "d"]) == ("d/a", set()) )

    # non-existant directories
    assert( try_find_best_path(["b"])      == (".",   {"b"}) )
    assert( try_find_best_path(["b", "c"]) == (".",   {"b", "c"}) )

    # combinations of the above
    assert( try_find_best_path(["b", "d"]) == ("d",   {"b"}) )

    # the ambiguous case
    # currently an arbitrary decision, and may vary from platform to platform
    r = try_find_best_path(["a", "b", "c"])
    assert( r == ("a/b", {"c"}) \
            or \
            r == ("a/c", {"b"}) )


def test_tag_add_dirs():
    # USE directories
    settings.use_dirs = True

    # don't add tags that are already present, and recompute dirs
    # also an ambiguous case (see note in test_dir_computer)
    r = try_add_remove("a/a_b_c", ["a"], [])
    assert( r == "a/b/c" \
            or \
            r == "a/c/b" )

    # don't move to a new directory unless ALL tags match
    r = try_add_remove("a/a_b_c", ["f"], [])
    assert( r == "a/b/f_c" \
            or \
            r == "a/c/f_b")


def test_tag_remove_dirs():
    # USE directories
    settings.use_dirs = True

    # general tag removal
    assert( try_add_remove("a/a_b_c", [], ["a"])      == "b_c" )
    assert( try_add_remove("f_g/a_b", [], ["a"])      == "f_g/b" )
    assert( try_add_remove("f_g/a_b", [], ["f", "g"]) == "a/b/" + settings.no_tags_filename )

    # tag removal causing tags in name to be used in dirs
    assert( try_add_remove("a/a_b_c",   [], ["c"])    == "a/b/" + settings.no_tags_filename )

    # tag removal from multi-tag directories
    assert( try_add_remove("f_g/a_b", [], ["f"])      == "a/b/g" )
    assert( try_add_remove("f_g/a_b", [], ["g"])      == "a/b/f" )
    assert( try_add_remove("f_g/a_b", [], ["f", "a"]) == "g_b" )
    assert( try_add_remove("f_g/a_b", [], ["f", "b"]) == "a/g" )
