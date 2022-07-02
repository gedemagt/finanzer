import os
from typing import Any

from appdata.app_dir_provider import AppDataDirProvider, StaticProvider
from appdata.repos import AppDataStore, JSONStore


class _AppData:

    def __init__(self):

        self._app_dir_provider: AppDataDirProvider = StaticProvider("app_data")

        self._store: AppDataStore = JSONStore("appdata.json")
        self._init_store()

    def __setitem__(self, key: str, value: Any):
        self._store.set_item(key, value)
        self._save()

    def __getitem__(self, key: str):
        return self._store.get_item(key)

    def _save(self):
        self._store.save()

    def set_store(self, store: AppDataStore):
        self._store = store
        self._init_store()

    def _init_store(self):
        self._store.set_path_builder(lambda x: self.from_app_data_dir(x, True))
        self._store.load()

    def set_app_dir_provider(self, provider: AppDataDirProvider):
        self._app_dir_provider = provider

    def from_app_data_dir(self, path: str, create_dir=False):
        result = self._app_dir_provider.get_in_app_dir(path)
        if create_dir:
            os.makedirs(result.parent, exist_ok=True)
        return result

    def ensure_app_data_exists(self):
        self._app_dir_provider.get_in_app_dir("").mkdir(parents=True, exist_ok=True)


appdata = _AppData()

set_store = appdata.set_store
set_app_dir_provider = appdata.set_app_dir_provider
from_app_data_dir = appdata.from_app_data_dir
ensure_app_data_exists = appdata.ensure_app_data_exists
