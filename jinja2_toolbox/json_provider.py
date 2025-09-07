from typing import TextIO, Any
import json

class JsonProvider:
    def load(self, f: TextIO) -> Any:
        return json.load(f)
