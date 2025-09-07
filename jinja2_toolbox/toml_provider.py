from typing import TextIO, Any
import toml

class TomlProvider:
    def load(self, f: TextIO) -> Any:
        return toml.load(f)
