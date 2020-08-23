import os
import shutil


def read_file(filename):
    with open(filename, 'r') as fin:
        return fin.read()


def remove_directory(name):
    if os.path.exists(name):
        shutil.rmtree(name)


def remove_files(filenames):
    for filename in filenames:
        if os.path.exists(filename):
            os.remove(filename)
