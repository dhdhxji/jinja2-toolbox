from jinja2.ext import Extension

class HappySadExt(Extension):
    def __init__(self, environment):
        environment.filters['happysad'] = self.__replace

    def __replace(self, value: str) -> str:
        return value.replace('=(', '=)')