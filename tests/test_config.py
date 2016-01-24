
from tagtool import get_config



def test_defaults():
    c = get_config()

    assert( c["root_dir"] == "")
    assert( c["use_dirs"] == False )
    assert( c["tag_delims"] )
    assert( c["default_delim"] == "_" )
    assert( c["no_tags_filename"] == "unknown" )
    assert( c["find_cmd"] and c["find_cmd"].startswith("find {dir} -type f {pattern}") )
    assert( c["case_sensitive"] == True )


def test_tagdir_lookup():
    c = get_config("tree/")

    print(c)

    assert( c["root_dir"] == "tree/")
    assert( c["use_dirs"] == True )
    assert( c["tag_delims"] )
    assert( c["default_delim"] == "_" )
    assert( c["no_tags_filename"] == "unknown" )
    assert( c["find_cmd"] and c["find_cmd"].startswith("find {dir} -type f {pattern}") )
    assert( c["case_sensitive"] == True )
