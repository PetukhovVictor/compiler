from ...combinators import Opt, Lazy
from ...AST.declarations.function import Function


def fun():
    """
    Parsing function statement.
    """
    from ..common import id, keyword, enumeration
    from ..statements import base

    def process(parsed):
        (((((((_, name), _), args), _), _), body), _) = parsed
        return Function(name, args, body)
    return keyword('fun') + id + \
        keyword('(') + Opt(enumeration()) + keyword(')') + \
           keyword('begin') + Opt(Lazy(base.stmt_list)) + \
        keyword('end') ^ process
