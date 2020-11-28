class LanguageError(Exception):

    def __init__(self, message, lineno, offset):
        self.message = message
        self.lineno = lineno
        self.offset = offset
