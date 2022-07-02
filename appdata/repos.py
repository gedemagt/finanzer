import orjson
from abc import ABC, abstractmethod
from json import JSONDecodeError
from typing import Any


class AppDataStore(ABC):

    def __init__(self):
        self._path_builder = lambda x: x

    def set_path_builder(self, builder):
        self._path_builder = builder

    def from_app_dir(self, path):
        return self._path_builder(path)

    @abstractmethod
    def save(self):
        pass

    @abstractmethod
    def load(self):
        pass

    @abstractmethod
    def set_item(self, key: str, value: Any) -> None:
        pass

    @abstractmethod
    def get_item(self, key: str) -> Any:
        pass


class JSONStore(AppDataStore):

    def __init__(self, path):
        super().__init__()
        self._path = path
        self._internal = {}

    def save(self):
        total_path = self.from_app_dir(self._path)
        with open(total_path, "w") as f:
            f.write(orjson.dumps(self._internal))

    def load(self) -> dict:
        try:
            total_path = self.from_app_dir(self._path)
            with open(total_path, "r") as f:
                self._internal = orjson.loads(f.read())
        except (FileNotFoundError, JSONDecodeError):
            return {}

    def set_item(self, key: str, value: Any) -> None:
        self._internal[key] = value

    def get_item(self, key: str) -> Any:
        return self._internal[key]
