"""
    pygments.lexers.web
    ~~~~~~~~~~~~~~~~~~~

    Just export previously exported lexers.

    :copyright: Copyright 2006-2021 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

from pygments.lexers.actionscript import ActionScript3Lexer
from pygments.lexers.actionscript import ActionScriptLexer
from pygments.lexers.actionscript import MxmlLexer
from pygments.lexers.css import CssLexer
from pygments.lexers.css import SassLexer
from pygments.lexers.css import ScssLexer
from pygments.lexers.data import JsonLexer
from pygments.lexers.html import DtdLexer
from pygments.lexers.html import HamlLexer
from pygments.lexers.html import HtmlLexer
from pygments.lexers.html import JadeLexer
from pygments.lexers.html import ScamlLexer
from pygments.lexers.html import XmlLexer
from pygments.lexers.html import XsltLexer
from pygments.lexers.javascript import CoffeeScriptLexer
from pygments.lexers.javascript import DartLexer
from pygments.lexers.javascript import JavascriptLexer
from pygments.lexers.javascript import LassoLexer
from pygments.lexers.javascript import LiveScriptLexer
from pygments.lexers.javascript import ObjectiveJLexer
from pygments.lexers.javascript import TypeScriptLexer
from pygments.lexers.php import PhpLexer
from pygments.lexers.webmisc import DuelLexer
from pygments.lexers.webmisc import QmlLexer
from pygments.lexers.webmisc import SlimLexer
from pygments.lexers.webmisc import XQueryLexer

JSONLexer = JsonLexer  # for backwards compatibility with Pygments 1.5

__all__ = []
