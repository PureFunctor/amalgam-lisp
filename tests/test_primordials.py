from amalgam.amalgams import (
    Atom,
    Environment,
    Function,
    Numeric,
    Quoted,
    SExpression,
    String,
    Symbol,
    Vector,
)
from amalgam.primordials import (
    FUNCTIONS,
    _add,
    _sub,
    _mul,
    _div,
    _setn,
    _fn,
    _mkfn,
    _bool,
)

from pytest import fixture, mark, param


@fixture
def env():
    return Environment(None, FUNCTIONS)


arithmetics = (
    param(
        arith_fn,
        arith_nm,
        arith_rs,
        id=f"({arith_op} {' '.join(map(str, arith_nm))})"
    )
    for arith_fn, arith_op, arith_nm, arith_rs in (
        (_add, "+", (1, 2), 1 + 2),
        (_add, "+", (1, 2, 3), 1 + 2 + 3),
        (_sub, "-", (5, 3), 5 - 3),
        (_sub, "-", (3, 5, 3), 3 - (5 + 3)),
        (_mul, "*", (2, 2), 2 * 2),
        (_mul, "*", (2, 2, 2), 2 * 2 * 2),
        (_div, "/", (4, 2), 4 / 2),
        (_div, "/", (6, 2, 3), 6 / (2 * 3)),
    )
)


@mark.parametrize(("arith_fn", "arith_nm", "arith_rs"), arithmetics)
def test_arithmetic_function(arith_fn, arith_nm, arith_rs):
    assert arith_fn(Environment(), *map(Numeric, arith_nm)).value == arith_rs


def test_setn(env):
    name = Symbol("name")
    amalgam = String("string")

    _setn_result = _setn(env, Quoted(name), Quoted(amalgam))

    assert env.iget("name") == amalgam
    assert _setn_result == amalgam


def test_fn(env):
    args = Vector(Symbol("x"), Symbol("y"))
    body = SExpression(Symbol("+"), Symbol("x"), Symbol("y"))

    _fn_result = _fn(env, Quoted(args), Quoted(body))

    assert _fn_result.fn(env, Numeric(21), Numeric(21)) == Numeric(42)


def test_mkfn(env):
    name = Symbol("name")
    args = Vector(Symbol("x"), Symbol("y"))
    body = SExpression(Symbol("+"), Symbol("x"), Symbol("y"))

    _mkfn_result = _mkfn(env, Quoted(name), Quoted(args), Quoted(body))

    assert env.iget("name") == _mkfn_result
    assert _mkfn_result.fn(env, Numeric(21), Numeric(21)) == Numeric(42)


bools = (
    param(bool_expr, bool_rslt, id=bool_iden)
    for bool_expr, bool_rslt, bool_iden in (
        (String(""), Atom("FALSE"), "empty-string"),
        (String("a"), Atom("TRUE"), "non-empty-string"),
        (Numeric(0), Atom("FALSE"), "zero-value"),
        (Numeric(42), Atom("TRUE"), "non-zero-value"),
        (Vector(), Atom("FALSE"), "empty-vector"),
        (Vector(Numeric(42)), Atom("TRUE"), "non-empty-vector"),
        (Atom("FALSE"), Atom("FALSE"), "false-atom"),
        (Atom("TRUE"), Atom("TRUE"), "true-atom"),
        (Atom("NIL"), Atom("FALSE"), "nil-atom"),
        (Atom("OTH"), Atom("TRUE"), "other-atom"),
    )
)


@mark.parametrize(("bool_expr", "bool_rslt"), bools)
def test_bool(env, bool_expr, bool_rslt):
    assert _bool(env, bool_expr) == bool_rslt
