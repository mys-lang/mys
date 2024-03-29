"""
    pygments.lexers.eiffel
    ~~~~~~~~~~~~~~~~~~~~~~

    Lexer for the Eiffel language.

    :copyright: Copyright 2006-2021 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

from pygments.lexer import RegexLexer
from pygments.lexer import include
from pygments.lexer import words
from pygments.token import Comment
from pygments.token import Keyword
from pygments.token import Name
from pygments.token import Number
from pygments.token import Operator
from pygments.token import Punctuation
from pygments.token import String
from pygments.token import Text

__all__ = ['EiffelLexer']


class EiffelLexer(RegexLexer):
    """
    For `Eiffel <http://www.eiffel.com>`_ source code.

    .. versionadded:: 2.0
    """
    name = 'Eiffel'
    aliases = ['eiffel']
    filenames = ['*.e']
    mimetypes = ['text/x-eiffel']

    tokens = {
        'root': [
            (r'[^\S\n]+', Text),
            (r'--.*?\n', Comment.Single),
            (r'[^\S\n]+', Text),
            # Please note that keyword and operator are case insensitive.
            (r'(?i)(true|false|void|current|result|precursor)\b', Keyword.Constant),
            (r'(?i)(and(\s+then)?|not|xor|implies|or(\s+else)?)\b', Operator.Word),
            (words((
                'across', 'agent', 'alias', 'all', 'as', 'assign', 'attached',
                'attribute', 'check', 'class', 'convert', 'create', 'debug',
                'deferred', 'detachable', 'do', 'else', 'elseif', 'end', 'ensure',
                'expanded', 'export', 'external', 'feature', 'from', 'frozen', 'if',
                'inherit', 'inspect', 'invariant', 'like', 'local', 'loop', 'none',
                'note', 'obsolete', 'old', 'once', 'only', 'redefine', 'rename',
                'require', 'rescue', 'retry', 'select', 'separate', 'then',
                'undefine', 'until', 'variant', 'when'), prefix=r'(?i)\b', suffix=r'\b'),
             Keyword.Reserved),
            (r'"\[([^\]%]|%(.|\n)|\][^"])*?\]"', String),
            (r'"([^"%\n]|%.)*?"', String),
            include('numbers'),
            (r"'([^'%]|%'|%%)'", String.Char),
            (r"(//|\\\\|>=|<=|:=|/=|~|/~|[\\?!#%&@|+/\-=>*$<^\[\]])", Operator),
            (r"([{}():;,.])", Punctuation),
            (r'([a-z]\w*)|([A-Z][A-Z0-9_]*[a-z]\w*)', Name),
            (r'([A-Z][A-Z0-9_]*)', Name.Class),
            (r'\n+', Text),
        ],
        'numbers': [
            (r'0[xX][a-fA-F0-9]+', Number.Hex),
            (r'0[bB][01]+', Number.Bin),
            (r'0[cC][0-7]+', Number.Oct),
            (r'([0-9]+\.[0-9]*)|([0-9]*\.[0-9]+)', Number.Float),
            (r'[0-9]+', Number.Integer),
        ],
    }
