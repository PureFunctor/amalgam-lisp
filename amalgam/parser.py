from fractions import Fraction
from functools import wraps
from io import StringIO
import re
from typing import Optional


import pyparsing as pp

import amalgam.amalgams as am


def apply_splat(func):
    """
    Helper function for splatting args to callbacks.

    Takes a callable `func` and return a function of one
    argument `tokens` and splats `tokens` into `func`.
    """

    @wraps(func)
    def _(tokens):
        return func(*tokens)

    return _


LPAREN, RPAREN, LBRACE, RBRACE = map(pp.Suppress, "()[]")

symbol_parser = pp.Regex(
    r"(?![+-]?[0-9])[\+\-\*/\\&<=>?!_a-zA-Z0-9]+"
).setParseAction(
    apply_splat(am.Symbol)
).setName("symbol")

_escaped_characters = (
    pp.Literal("\\")
    + (
        pp.Literal("\\")
        | pp.Literal("\"")
        | pp.CharsNotIn("\\\"").setResultsName("character")
    )
).setParseAction(
    lambda tokens: tokens.character if tokens.character else tokens
)

_regular_characters = pp.CharsNotIn("\\\"")

_string_contents = pp.Combine(
    (_escaped_characters | _regular_characters)[...]
).leaveWhitespace()

string_parser = (
    pp.Suppress("\"") + _string_contents + pp.Suppress("\"")
).setParseAction(
    apply_splat(am.String)
).setName("string")

_string_integral_parser = pp.Regex(r"[+-]?(0|[1-9]\d*)")

_integral_parser = _string_integral_parser.copy().setParseAction(
    apply_splat(int)
)

_floating_parser = pp.Combine(
    _string_integral_parser + pp.Literal(".") + pp.Regex(r"\d+")
).setParseAction(
    apply_splat(float)
)

_fraction_parser = (
    _integral_parser
    + pp.Suppress("/").leaveWhitespace()
    + _integral_parser.copy().leaveWhitespace()
).setParseAction(
    apply_splat(Fraction)
)

numeric_parser = (
    _floating_parser | _fraction_parser | _integral_parser
).setParseAction(
    apply_splat(am.Numeric)
).setName("numeric")

expression_parser = pp.Forward()

quoted_parser = (
    pp.Suppress("'") + expression_parser
).setParseAction(
    apply_splat(am.Quoted)
).setName("quoted")

s_expression_parser = (
    LPAREN + expression_parser[...] + RPAREN
).setParseAction(
    apply_splat(am.SExpression)
).setName("s-expression")

vector_parser = (
    LBRACE + expression_parser[...] + RBRACE
).setParseAction(
    apply_splat(am.Vector)
).setName("vector")

expression_parser <<= (
    quoted_parser
    | numeric_parser
    | symbol_parser
    | string_parser
    | s_expression_parser
    | vector_parser
)


class AmalgamParser:
    """
    Class that serves as the parsing frontend.

    The `parse` method allows for reentrant parsing of text by
    utilizing a `StringIO` buffer; this enables the REPL to be
    able to parse multi-line expressions by checking for the
    return value of said method.
    """

    inst = None

    def __new__(cls) -> "AmalgamParser":
        if cls.inst is not None:
            return cls.inst

        self = super().__new__(cls)
        cls.inst = self

        return cls.inst

    def __init__(self) -> None:
        self.parse_buffer = StringIO()
        self.expect_more = False

        string_parser.setFailAction(self._expect_more)
        s_expression_parser.setFailAction(self._expect_more)
        vector_parser.setFailAction(self._expect_more)

    def _expect_more(self, *arguments) -> None:
        *_, err = arguments
        if re.match(r"Expected \"[\)\]\"]\", found end of text", str(err)):
            self.expect_more = True

    def parse(self, text: str) -> Optional[am.Amalgam]:
        self.parse_buffer.write(text)
        self.parse_buffer.seek(0)
        self.expect_more = False

        text = self.parse_buffer.read()

        try:
            expr = expression_parser.parseString(text, parseAll=True)[0]

        except pp.ParseException as p:
            if not self.expect_more:
                self.parse_buffer = StringIO()
                raise p
            return None

        else:
            self.parse_buffer = StringIO()
            return expr
