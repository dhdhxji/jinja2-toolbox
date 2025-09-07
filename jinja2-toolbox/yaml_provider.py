from typing import TextIO, Any
import yaml

class YamlProvider:
    def load(self, f: TextIO) -> Any:
        # TODO: Think if unsafe load? The tool may leverage that 
        # to execute custom python code...
        return yaml.safe_load(f)
