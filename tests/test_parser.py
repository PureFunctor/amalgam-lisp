from fractions import Fraction

import amalgam.amalgams as am
import amalgam.parser as pr

from pyparsing import ParseException
from pytest import raises


def test_symbol_parser_allowed_characters():
    text = r"-+*/<?Spam21&+-*/\&<=>?!_=42Eggs!>\*+-"
    assert pr.symbol_parser.parseString(text)[0] == am.Symbol(text)


def test_symbol_parser_raises_ParseException_on_negative_number():
    with raises(ParseException):
        pr.symbol_parser.parseString("-1")


def test_symbol_parser_raises_ParseException_on_positive_number():
    with raises(ParseException):
        pr.symbol_parser.parseString("+1")


def test_numeric_parser_integral():
    parse_func = pr.numeric_parser.parseString

    unsigned = parse_func("42")[0]
    positive = parse_func("+42")[0]

    assert unsigned == positive == am.Numeric(42)


def test_numeric_parser_floating():
    parse_func = pr.numeric_parser.parseString

    unsigned = parse_func("21.42")[0]
    positive = parse_func("+21.42")[0]

    assert unsigned == positive == am.Numeric(21.42)


def test_numeric_parser_fraction():
    from functools import reduce
    from operator import eq

    parse_func = pr.numeric_parser.parseString

    positives = [
        parse_func(f"{n}/{d}")[0]
        for n in ("21", "+21")
        for d in ("42", "+42")
    ]

    return all(am.Numeric(Fraction(21,42)) == positive for positive in positives)


def test_numeric_parser_integral_negative():
    assert pr.numeric_parser.parseString("-42")[0] == am.Numeric(-42)


def test_numeric_parser_floating_negative():
    assert pr.numeric_parser.parseString("-21.42")[0] == am.Numeric(-21.42)


def test_numeric_parser_fraction_negative_numerator():
    assert pr.numeric_parser.parseString("-21/42")[0] == am.Numeric(Fraction(-21, 42))


def test_numeric_parser_fraction_negative_denominator():
    assert pr.numeric_parser.parseString("21/-42")[0] == am.Numeric(Fraction(21, -42))


def test_numeric_parser_fraction_negative_num_denom():
    assert pr.numeric_parser.parseString("-21/-42")[0] == am.Numeric(Fraction(-21, -42))


def test_numeric_parser_floating_raises_ParseException_on_space():
    with raises(ParseException):
        pr.numeric_parser.parseString("21. 42", parseAll=True)

    with raises(ParseException):
        pr.numeric_parser.parseString("21 .42", parseAll=True)


def test_numeric_parser_fraction_raises_ParseException_on_space():
    with raises(ParseException):
        pr.numeric_parser.parseString("21/ 42", parseAll=True)

    with raises(ParseException):
        pr.numeric_parser.parseString("21 /42", parseAll=True)
