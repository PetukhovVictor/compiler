from src.Parser.Parsers.arithmetic_exprs import aexp
from src.Parser.Parsers.basic import *
from src.Parser.Parsers.boolean_exprs import bexp, bexp_relop

from src.Parser.AST.statements import *

"""
Parsing simple assign statement.
Example: x := 56
"""
def assign_stmt():
    def process(parsed):
        ((name, _), exp) = parsed
        return AssignStatement(name, exp)
    return id + keyword(':=') + (bexp() | aexp() | read_stmt()) ^ process

"""
Parsing statement list (by ';' separator).
Example:
x := 56;
y := 12;
z := 512
"""
def stmt_list():
    separator = keyword(';') ^ (lambda x: lambda l, r: CompoundStatement(l, r))
    return Exp(stmt(), separator)

"""
Parsing 'if' statement.
"""
def if_stmt():
    def process(parsed):
        (((((_, condition), _), true_stmt), false_parsed), _) = parsed
        if false_parsed:
            (_, false_stmt) = false_parsed
        else:
            false_stmt = None
        return IfStatement(condition, true_stmt, false_stmt)
    return keyword('if') + bexp() + \
           keyword('then') + Lazy(stmt_list) + \
           Opt(keyword('else') + Lazy(stmt_list)) + \
           keyword('fi') ^ process

"""
Parsing 'while' statement.
"""
def while_stmt():
    def process(parsed):
        ((((_, condition), _), body), _) = parsed
        return WhileStatement(condition, body)
    return keyword('while') + bexp() + \
           keyword('do') + Lazy(stmt_list) + \
           keyword('od') ^ process

"""
Parsing 'repeat' statement.
"""
def repeat_stmt():
    def process(parsed):
        (((_, body), _), condition) = parsed
        return RepeatStatement(condition, body)
    return keyword('repeat') + Lazy(stmt_list) + \
        keyword('until') + bexp() ^ process

"""
Parsing 'read' statement.
"""
def read_stmt():
    return keyword('read') + keyword('(') + keyword(')') ^ (lambda parsed: ReadStatement())

"""
Parsing 'write' statement.
"""
def write_stmt():
    def process(parsed):
        (((_, _), name), _) = parsed
        return WriteStatement(name)
    return keyword('write') + \
        keyword('(') + aexp() + keyword(')') ^ process

"""
Main statement parser.
Try to first parse as 'assign' statement,
if not possible - as 'if' statement,
if not possible - as 'while' statement.
"""
def stmt():
    return assign_stmt() | \
           if_stmt() | \
           while_stmt() | \
           repeat_stmt() | \
           write_stmt()
