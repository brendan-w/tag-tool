#!/usr/bin/env python3


import sys


find_cmd = "find . -type f -path \"*\" ! -path \"*/.*\" ! -perm -o=x";



help_text = """
Usage:
\ttag-find [OPTION...] [SELECTOR...]

Selectors:
\t[TAG]    filters tagged files for this tag         ("AND")
\t+[TAG]   adds tagged files to the selection        ("OR")
\t-[TAG]   removes tagged files from the selection   ("NOT")

Options:
\t--help   prints this help text and exits

For issues and documentation: https://github.com/brendanwhitfield/tag-tool
"""



def main():

    # the 3 types of selection operations
    tag_intersections = set()
    tag_additions     = set()
    tag_exclusions    = set()

    for option in sys.argv[1:]:
        if option == "--help":
            print(help_text)
            return
        else:
            if option[0] == "+":
                tag_additions.add(option[1:])
            elif option[0] == "-":
                tag_exclusions.add(option[1:]);
            else:
                tag_intersections.add(option)

    # check that the user entered something
    if (len(tag_intersections) +
        len(tag_additions) +
        len(tag_exclusions)) == 0:
        print("please give tag selectors")
        return


    # run the tagger
    run(tag_intersections, tag_additions, tag_exclusions)


if(__name__ == "__main__"):
    main()
