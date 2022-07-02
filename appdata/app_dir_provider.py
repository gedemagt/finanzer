from abc import ABC, abstractmethod
from pathlib import Path

from appdirs import AppDirs


class AppDataDirProvider(ABC):

    @abstractmethod
    def get_in_app_dir(self, path: str):
        pass


class AppDirsProvider(AppDataDirProvider):

    def __init__(self, app_dirs: AppDirs):
        super().__init__()
        self._app_dirs = app_dirs

    def get_in_app_dir(self, path: str):
        parent = Path(self._app_dirs.user_data_dir)
        return parent / path


class StaticProvider(AppDataDirProvider):

    def __init__(self, path):
        self._parent = Path(path)

    def get_in_app_dir(self, path: str):
        return self._parent / path
