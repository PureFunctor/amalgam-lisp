from dataclasses import fields
from functools import partial

import amalgam.amalgams as am
import unittest.mock as mk


class AmalgamMockMixin:
    """
    Mixin for creating a custom `Mock` for an `Amalgam`.

    Modifies `Mock._get_child_mock` to return a `MagicMock`
    instance instead of the parent class. Also frees the
    `name` keyword from being tightly bound as a parameter
    for `Mock`, and allows it to be used by the subclasses
    instead. As such, `__mock_name` can be used to set the
    name of the `Mock`.
    """

    spec_set = None

    def __init__(self, **keywords):
        mock_name = keywords.pop("__mock_name", "mock")

        super().__init__(spec_set=self.spec_set, name=mock_name, **keywords)

    def _get_child_mock(self, **keywords):
        return mk.MagicMock(**keywords)


class ValueAmalgamMixin:
    """Mixin for `Amalgam` subclasses that are instantiated with `value`."""

    def __init__(self, value=None, **keywords):
        super().__init__(**keywords)
        self.value = value if value is not None else mk.MagicMock()


class VariadicAmalgamMixin:
    """Mixin for `Amalgam` subclasses that are instantiated with `vals`."""

    def __init__(self, *vals, **keywords):
        super().__init__(**keywords)
        self.vals = vals if len(vals) > 0 else mk.MagicMock()


class MockEnvironment(AmalgamMockMixin, mk.MagicMock):
    """Mocks an `Environment`."""
    spec_set = am.Environment(mk.MagicMock(), mk.MagicMock())


class MockSymbol(ValueAmalgamMixin, AmalgamMockMixin, mk.MagicMock):
    """Mocks a `Symbol` `Amalgam`."""
    spec_set = am.Symbol(mk.MagicMock())


class MockString(ValueAmalgamMixin, AmalgamMockMixin, mk.MagicMock):
    """Mocks a `String` `Amalgam`."""
    spec_set = am.String(mk.MagicMock())


class MockNumeric(ValueAmalgamMixin, AmalgamMockMixin, mk.MagicMock):
    """Mocks a `Numeric` `Amalgam`."""
    spec_set = am.Numeric(mk.MagicMock())


class MockFunction(AmalgamMockMixin, mk.MagicMock):
    """Mocks a `Function` `Amalgam`."""
    spec_set = am.Function(mk.MagicMock(), mk.MagicMock(), mk.MagicMock())

    def __init__(self, name=None, fn=None, defer=False, **keywords):
        super().__init__(**keywords)

        self.name = name if name is not None else mk.MagicMock()
        self.fn = fn if fn is not None else mk.MagicMock()
        self.defer = defer if defer is not None else mk.MagicMock()


class MockQuoted(ValueAmalgamMixin, AmalgamMockMixin, mk.MagicMock):
    """Mocks a `Quoted` `Amalgam`."""
    spec_set = am.Quoted(mk.MagicMock())


class MockSExpression(VariadicAmalgamMixin, AmalgamMockMixin, mk.MagicMock):
    """Mocks an `SExpression` `Amalgam`."""
    spec_set = am.SExpression(mk.MagicMock(), mk.MagicMock())


class MockVector(VariadicAmalgamMixin, AmalgamMockMixin, mk.MagicMock):
    """Mocks a `Vector` `Amalgam`."""
    spec_set = am.Vector(mk.MagicMock(), mk.MagicMock())
