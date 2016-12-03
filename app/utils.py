import os

def make_directory_tree(path):
    if not os.path.exists(path):
        make_directory_tree(os.path.dirname(path))
        try:
            os.mkdir(path)
        except FileExistsError as e:
            pass
