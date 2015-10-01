#!/usr/bin/env python3

import os
from tag import *

cwd = os.getcwd()


# DON'T use_dirs
test_options(cwd, False)


assert(run_for_file(
  set([]), #add_tags
  set(["a"]), #remove_tags
     "/home/brendan/tag-tool/a_ab/a_ab/a_ab_a_ba_a.txt" # file
) == "/home/brendan/tag-tool/a_ab/a_ab/ab_ba.txt")

assert(run_for_file(
  set([]), #add_tags
  set(["a", "ab", "ba"]), #remove_tags
     "/home/brendan/tag-tool/a_ab_a_ba_a.txt" # file
) == "/home/brendan/tag-tool/%s.txt" % no_tags_filename)


# use_dirs
test_options(cwd, True)


assert(run_for_file(
  set([]), #add_tags
  set(["a"]), #remove_tags
     "/home/brendan/tag-tool/a_ab/a_ab/a_ab_a_ba_a.txt" # file
) == "/home/brendan/tag-tool/ab/ab/ab_ba.txt")


# test the dir computers

"""
test_tree/
├── a/
│   ├── b/
│   └── c/
└── d/
    ├── a/
    └── e/
"""

r = find_best_path("test_tree", set(["a"]))
assert(r[0] == "test_tree/a")
assert(r[1] == set())


r = find_best_path("test_tree", set(["a", "b"]))
assert(r[0] == "test_tree/a/b")
assert(r[1] == set())


r = find_best_path("test_tree", set(["a", "b", "f", "g"]))
assert(r[0] == "test_tree/a/b")
assert(r[1] == set(["f", "g"]))


r = find_best_path("test_tree", set(["a", "d"]))
assert(r[0] == "test_tree/d/a")
assert(r[1] == set())


r = find_best_path("test_tree", set(["e"]))
assert(r[0] == "test_tree")
assert(r[1] == set(["e"]))




print("All tests passed")
