import os

def print_tree(start_path='.', ignore=None, prefix=''):
    """
    Recursively prints the folder structure in a tree-like format.

    Args:
        start_path (str): Root directory to start printing from.
        ignore (list[str]): List of folders/files to ignore.
        prefix (str): Used internally for indentation.
    """
    if ignore is None:
        ignore = ['.venv', '__pycache__', '.git', '.idea']

    for item in sorted(os.listdir(path=start_path)):
        if item in ignore:
            continue
        path = os.path.join(start_path, item)
        print(prefix + item)
        if os.path.isdir(s=path):
            print_tree(start_path=path, ignore=ignore, prefix=prefix + '    ')
            
if __name__ == '__main__':
    print_tree('.')