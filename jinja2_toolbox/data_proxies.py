from typing import Any, Union
from collections.abc import Mapping, Sequence
import typing
import inspect


def wrap_type_into_rich_proxy(
        cls: typing.Type,
        bases: typing.Iterable[typing.Type] = tuple(),
        overrides: dict[str, typing.Callable] = {}) -> typing.Type:
    def __init__(self, value: Any, parent: Any) -> None:
        object.__setattr__(self, 'value', value)
        object.__setattr__(self, 'parent', parent)

    def __getattribute__(self, name):
        if name == 'parent':
            return object.__getattribute__(self, 'parent')
        elif name == 'depleted':
            return object.__getattribute__(self, 'value')
        else:
            # TODO: Try to enrich here?
            return object.__getattribute__(self, 'value').__getattribute__(name)

    static_attrs = {
        '__init__': __init__,
        '__getattribute__': __getattribute__,
        **overrides
    }

    attr_whitelist = tuple((
        '__add__', '__contains__', '__delattr__', '__doc__', '__eq__',
        '__format__', '__ge__', '__getitem__', '__getslice__', '__gt__',
        '__hash__', '__le__', '__len__', '__lt__', '__mod__', '__mul__',
        '__ne__', '__reduce__', '__reduce_ex__', '__repr__', '__rmod__',
        '__rmul__', '__setattr__', '__str__', '__iter__'
    ))

    # TODO: Test out are functions accessible from jinja?
    def forward_call(name) -> Any:
        def call(self, *args, **kwargs) -> Any:
            return object.__getattribute__(self, 'value').__getattribute__(name)(*args, **kwargs)

        return call

    dynamic_attrs = {
        name: forward_call(name)
        for name, _func in inspect.getmembers(cls, inspect.isroutine)
        if name not in static_attrs
        if name in attr_whitelist
    }

    return type(f'_JinjaToolboxRichProxy_{cls.__name__}', (bases), {
        **static_attrs,
        **dynamic_attrs,
    })


def enrich(d: Any, parent: Any = None) -> Any:
    t = type(d)
    if t.__name__.startswith('_JinjaToolboxRichProxy'):
        return d
    elif isinstance(d, Mapping):
        return wrap_type_into_rich_proxy(t, bases=(Mapping,), overrides={
            '__getitem__': lambda self, key: enrich(object.__getattribute__(self, 'value')[key], self),
        })(d, parent)
    elif isinstance(d, Sequence):
        return wrap_type_into_rich_proxy(t, bases=(Sequence,), overrides={
            '__getitem__': lambda self, key: enrich(object.__getattribute__(self, 'value')[key], self),
        })(d, parent)
    elif isinstance(d, (int, float, str, bool)):
        return wrap_type_into_rich_proxy(t)(d, parent)
    else:
        raise RuntimeError(f'Unsupported data type {type(d)} for wrapping')


def deplete(d: Any) -> Union[map, tuple, list, int, float, str]:
    return d.depleted
