from pegen import grammar
from pegen.grammar import Alt
from pegen.grammar import Cut
from pegen.grammar import Gather
from pegen.grammar import GrammarVisitor
from pegen.grammar import Group
from pegen.grammar import Lookahead
from pegen.grammar import NamedItem
from pegen.grammar import NameLeaf
from pegen.grammar import NegativeLookahead
from pegen.grammar import Opt
from pegen.grammar import PositiveLookahead
from pegen.grammar import Repeat0
from pegen.grammar import Repeat1
from pegen.grammar import Rhs
from pegen.grammar import Rule
from pegen.grammar import StringLeaf


class ValidationError(Exception):
    pass

class GrammarValidator(GrammarVisitor):
    def __init__(self, grammar: grammar.Grammar):
        self.grammar = grammar
        self.rulename = None

    def validate_rule(self, rulename: str, node: Rule):
        self.rulename = rulename
        self.visit(node)
        self.rulename = None


class SubRuleValidator(GrammarValidator):
    def visit_Rhs(self, node: Rule):
        for index, alt in enumerate(node.alts):
            alts_to_consider = node.alts[index+1:]
            for other_alt in alts_to_consider:
                self.check_intersection(alt, other_alt)

    def check_intersection(self, first_alt: Alt, second_alt: Alt) -> bool:
        if str(second_alt).startswith(str(first_alt)):
            raise ValidationError(
                    f"In {self.rulename} there is an alternative that will "
                    f"never be visited:\n{second_alt}")

def validate_grammar(the_grammar: grammar.Grammar):
    for validator_cls in GrammarValidator.__subclasses__():
        validator = validator_cls(the_grammar)
        for rule_name, rule in the_grammar.rules.items():
            validator.validate_rule(rule_name, rule)
