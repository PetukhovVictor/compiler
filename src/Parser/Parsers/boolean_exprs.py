from src.Parser.Parsers.arithmetic_exprs import aexp, any_operator_in_list, precedence, process_group
from src.Parser.Parsers.basic import *

from src.Parser.AST.boolean_exprs import *
from src.Parser.AST.arithmetic_exprs import IntAexp

"""
Precedence levels for binary operations.
"""
bexp_precedence_levels = [
    ['&&'],
    ['||'],
]

"""
Convert boolean expression value to object of AST-class 'RelopBexp'.
"""
def process_relop(parsed):
    ((left, op), right) = parsed
    return RelopBexp(op, left, right)

"""
Convert single value to object of AST-class 'RelopBexp' with '==' operator and '0' right value.
"""
def process_boolop(parsed):
    return RelopBexp('==', parsed, IntAexp(0))

"""
Parsing boolean expression (arithmetic expression + compare operator + arithmetic expression).
"""
def bexp_relop():
    relops = ['<', '<=', '>', '>=', '==', '!=']
    return (aexp() ^ process_boolop) | (aexp() + any_operator_in_list(relops) + aexp() ^ process_relop)

"""
Parsing 'not' expression (convert expression to object of AST-class 'NotBexp').
"""
def bexp_not():
    return keyword('!') + Lazy(bexp_term) ^ (lambda parsed: NotBexp(parsed[1]))

"""
Parse the binary expression in parentheses.
"""
def bexp_group():
    return keyword('(') + Lazy(bexp) + keyword(')') ^ process_group

"""
Parse the binary expression.
Try to first parse as 'not' expression,
if not possible - as just binary expressions,
if not possible - as a parentheses group of binary expressions.
"""
def bexp_term():
    return bexp_not() | bexp_relop() | bexp_group()

"""
Parse the binary operation binary expression.
Convert operator to fabric of AST-classes 'AndBexp' / 'OrBexp'.
"""
def process_logic(op):
    if op == '&&':
        return lambda l, r: AndBexp(l, r)
    elif op == '||':
        return lambda l, r: OrBexp(l, r)
    else:
        raise RuntimeError('unknown logic operator: ' + op)

"""
Main binary expressions parser.
"""
def bexp():
    return precedence(bexp_term(),
                      bexp_precedence_levels,
                      process_logic)
