import re

class LanguageError(Exception):

    def __init__(self, message, lineno, offset):
        self.message = message
        self.lineno = lineno
        self.offset = offset

SNAKE_CASE_RE = re.compile(r'^(_*[a-z][a-z0-9_]*)$')
UPPER_SNAKE_CASE_RE = re.compile(r'^(_*[A-Z][A-Z0-9_]*)$')
PASCAL_CASE_RE = re.compile(r'^_?[A-Z][a-zA-Z0-9]*$')

def is_snake_case(value):
    return SNAKE_CASE_RE.match(value) is not None

def is_upper_snake_case(value):
    return UPPER_SNAKE_CASE_RE.match(value) is not None

def is_pascal_case(value):
    return PASCAL_CASE_RE.match(value)
