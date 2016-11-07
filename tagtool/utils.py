
import os
import shutil


# recursively finds the nearest .tagdir file denoting the limit for moving files
def find_above(path, filename):
    if os.path.isfile(os.path.join(path, filename)):
        return path
    else:
        if not path or path == "/":
            return ""
        else:
            return find_above(os.path.dirname(path), filename)


# lists only directories at the given path
def dirs_at(path):
    return [ name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name)) ]

# deletes all symlinks in the given directory [ USE WITH CAUTION ]
def empty_links_dir(path):
    for f in os.listdir(path):
        file_path = os.path.join(path, f)
        if os.path.islink(file_path):
            os.unlink(file_path)

def find_all_files(path):
    files = set()
    for root, directories, filenames in os.walk(path):
        for f in filenames:
            files.add(os.path.join(root, f))
    return files
