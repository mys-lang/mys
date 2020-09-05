import re
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

def remove_ansi(string):
    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')

    return ansi_escape.sub('', string)
