from typing import Any, Dict, Union, List
from collections.abc import Mapping, Iterable
from dataclasses import dataclass

@dataclass
class PlainValueProxy:
    __value: Any
    parent: Union['MappingProxy', 'ListProxy']

    def __repr__(self):
        return self.__value.__repr__()
    
    def __str__(self):
        return self.__value.__str__()

    @property
    def deplete(self):
        return self.__value

@dataclass
class ListProxy(Iterable):
    __value: List
    parent: Union['MappingProxy', 'ListProxy']

    def __getitem__(self, key: Any) -> Any:
        return wrap(self.__value[key], self)

    def __iter__(self) -> Any:
        yield from map(lambda i: wrap(i, self), self.__value)

    def __len__(self) -> int:
        return len(self.__value)

    def __repr__(self):
        return self.__value.__repr__()
    
    def __str__(self):
        return self.__value.__str__()

    @property
    def deplete(self):
        return self.__value

@dataclass
class MappingProxy(Mapping):
    __value: Dict[Any, Any]
    parent: Union['MappingProxy', 'ListProxy']

    def __getitem__(self, key: Any) -> Any:
        return wrap(self.__value[key], self)

    def __iter__(self) -> Any:
        # We iterate throuhh the keys here, so no need to wrap anything
        yield from self.__value

    def __len__(self) -> int:
        return len(self.__value)

    def __repr__(self):
        return self.__value.__repr__()
    
    def __str__(self):
        return self.__value.__str__()

    @property
    def deplete(self):
        return self.__value



def wrap(d: Any, parent: MappingProxy=None) -> Union[MappingProxy, ListProxy, PlainValueProxy]:
    t = type(d)
    if t == dict:
        # TODO: Check is key does not exit in the data
        return MappingProxy(d, parent)
    elif t == tuple or t == list:
        return ListProxy(d, parent)
    elif t == int or t == float or t == str or t == bool or d == None:
        return PlainValueProxy(d, parent)
    else:
        raise RuntimeError(f'Unsupported data type {type(d)} for wrapping')
