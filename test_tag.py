#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

# move into our test_tree directory
os.chdir("test_tree")
cwd = os.getcwd()

from tag import *


"""
test_tree/
├── a/
│   ├── a_b_c
│   ├── b/
│   │   └── .gitkeep
│   └── c/
│       └── .gitkeep
├── d/
│   ├── a/
│   │   └── .gitkeep
│   └── e/
│       └── .gitkeep
├── f_g/
│   └── a_b_c
└── .tagdir
"""


def try_add_remove(f, add_tags, remove_tags):
    f = File(os.path.join(cwd, f))
    f.add_remove_tags(add_tags, remove_tags)
    return os.path.relpath(str(f), cwd)


def try_find_best_path(tags):
    r = find_best_path(cwd, set(tags))
    return (os.path.relpath(r[0], cwd), r[1])




def test_tag_add_name():
    # DON'T use_dirs
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
    # DON'T use_dirs
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



def test_dir_computer():

    # simple finding of directories
    assert( try_find_best_path(["a"])      == ("a",   set([])) )
    assert( try_find_best_path(["a", "b"]) == ("a/b", set([])) )
    assert( try_find_best_path(["a", "d"]) == ("d/a", set([])) )

    # non-existant directories
    assert( try_find_best_path(["b"])      == (".",   set(["b"])) )
    assert( try_find_best_path(["b", "c"]) == (".",   set(["b", "c"])) )

    # combinations of the above
    assert( try_find_best_path(["a", "b", "c"]) == ("a/b", set(["c"])) )
    assert( try_find_best_path(["b", "d"])      == ("d",   set(["b"])) )


def test_tag_add_dirs():
    # USE directories
    settings.use_dirs = True

    # don't add tags that are already present, and recompute dirs
    assert( try_add_remove("a/a_b_c", ["a"], []) == "a/b/c" )

    # recompute paths
    assert( try_add_remove("a/a_b_c", ["d"], [])      == "a/b/d_c" )
    assert( try_add_remove("a/a_b_c", ["d", "e"], []) == "a/b/e_d_c" )


def test_tag_remove_dirs():
    # USE directories
    settings.use_dirs = True

    # general tag removal
    assert( try_add_remove("a/a_b_c",   [], ["a"])      == "b_c" )
    assert( try_add_remove("f_g/a_b_c", [], ["a"])      == "f_g/b_c" )
    assert( try_add_remove("f_g/a_b_c", [], ["f", "g"]) == "a/b/c" )

    # tag removal from multi-tag directories
    assert( try_add_remove("f_g/a_b_c", [], ["f"]) == "a/b/g_c" )
    assert( try_add_remove("f_g/a_b_c", [], ["g"]) == "a/b/f_c" )
    assert( try_add_remove("f_g/a_b_c", [], ["f", "a"]) == "g_b_c" )
    assert( try_add_remove("f_g/a_b_c", [], ["f", "b"]) == "a/c/g" )
