#!/usr/bin/env python3

import os
from tag import *

cwd = os.getcwd()

test_options(cwd, False)
assert(run_for_file(
  set([]), #add_tags
  set(["a"]), #remove_tags
     "/home/brendan/tag-tool/a_ab/a_ab/a_ab_a_ba_a.txt" # file
) == "/home/brendan/tag-tool/a_ab/a_ab/ab_ba.txt")


test_options(cwd, True)
assert(run_for_file(
  set([]), #add_tags
  set(["a"]), #remove_tags
     "/home/brendan/tag-tool/a_ab/a_ab/a_ab_a_ba_a.txt" # file
) == "/home/brendan/tag-tool/ab/ab/ab_ba.txt")
