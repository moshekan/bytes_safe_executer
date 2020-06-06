from contextlib import contextmanager
import shutil
import tempfile
import os


def copy_files(files: list, dest_dir: str):
    for filename in files or ():
        dest = os.path.join(dest_dir, os.path.basename(filename))
        if os.path.islink(filename):
            os.symlink(os.readlink(filename), dest)
        elif os.path.isfile(filename):
            shutil.copy(filename, dest_dir)
        else:
            shutil.copytree(filename, dest, symlinks=True)


@contextmanager
def create_temp_dir():
    """
    A context manager for a temp dir. Removes the dir when exits.
    """
    temp_dir = tempfile.mkdtemp(prefix="safe_execute_")
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir)


def get_temp_dir():
    """
    A context manager for a temp dir. Removes the dir when exits.
    """
    return tempfile.mkdtemp(prefix="safe_execute_")