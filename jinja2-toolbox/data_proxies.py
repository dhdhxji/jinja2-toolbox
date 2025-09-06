from typing import Any, Dict, Union, List
from collections.abc import Mapping, Iterable
from dataclasses import dataclass

@dataclass
class PlainValueProxy:
    value: Any
    parent: Union['MappingProxy', 'ListProxy']

    def __repr__(self):
        return self.value.__repr__()

@dataclass
class ListProxy(Iterable):
    contents: List
    parent: Union['MappingProxy', 'ListProxy']

    def __getitem__(self, key: Any) -> Any:
        return self.contents[key]

    def __iter__(self) -> Any:
        yield from self.contents

    def __len__(self) -> int:
        return len(self.contents)

    def __repr__(self):
        return str(self.contents)

@dataclass
class MappingProxy(Mapping):
    contents: Dict[Any, Any]
    parent: Union['MappingProxy', 'ListProxy']

    def __getitem__(self, key: Any) -> Any:
        return self.contents[key]

    def __iter__(self) -> Any:
        yield from self.contents

    def __len__(self) -> int:
        return len(self.contents)

    def __repr__(self):
        return self.contents.__repr__()
    



def _wrap(d: Any, parent: MappingProxy=None) -> Union[MappingProxy, ListProxy, PlainValueProxy]:
    t = type(d)
    if t == dict:
        # TODO: Check is key does not exit in the data
        result = MappingProxy(None, parent)
        result.contents = {
            key: _wrap(value, result)
            for key, value in d.items()
        }

        return result
    elif t == tuple or t == list:
        result = ListProxy(None, parent)
        result.contents = tuple((
            _wrap(value, result)
            for value in d
        ))

        return result
    elif t == int or t == float or t == str or t == bool or d == None:
        return PlainValueProxy(d, parent)
    else:
        raise RuntimeError(f'Unsupported data type {type(d)} for wrapping')
    
def wrap(d: Any) -> Union[MappingProxy, PlainValueProxy]:
    return _wrap(d, None)