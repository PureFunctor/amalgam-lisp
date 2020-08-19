from fractions import Fraction
import re
from typing import Any

from amalgam.amalgams import (
    create_fn,
    Amalgam,
    Environment,
    Function,
    Numeric,
    String,
)

from pytest import fixture


@fixture
def num():
    return Numeric(42)


@fixture
def numerics():
    return Numeric(21), Numeric(21.42), Numeric(Fraction(21, 42))


@fixture
def strings():
    return String(""), String("\n\t"), String("foo-bar-baz")


@fixture
def env():
    return Environment()


def _common_repr(inst: Amalgam):
    return fr"<{inst.__class__.__name__} '[\s\S]+' @ {hex(id(inst))}>"


def test_numeric_evaluate(numerics):
    for numeric in numerics:
        assert numeric == numeric.evaluate(Environment())


def test_numeric_repr(numerics):
    for numeric in numerics:
        assert re.match(_common_repr(numeric), repr(numeric))


def test_string_evaluate(strings):
    for string in strings:
        assert string == string.evaluate(Environment())


def test_string_repr(strings):
    for string in strings:
        assert re.match(_common_repr(string), repr(string))


def test_function_evaluate_binding(num, env):
    fnc = create_fn("binding-test", "_x", num)
    assert fnc.evaluate(env).env == env


def test_function_evaluate_literal(num, env):
    fnc = create_fn("literal-test", "_x", num)
    assert fnc.evaluate(env).call(num).value == num.value
