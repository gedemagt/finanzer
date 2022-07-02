import json
from abc import ABC, abstractmethod
from json import JSONDecodeError
from typing import List, Dict

import appdata
from finance.model.entry import Budget


class BudgetRepo(ABC):

    @abstractmethod
    def save_budget(self, budget: Budget) -> None:
        pass

    @abstractmethod
    def get_budgets(self) -> List[Budget]:
        pass

    @abstractmethod
    def get_budget(self, name: str) -> Budget:
        pass


class DocumentRepo(BudgetRepo):

    def __init__(self, path="budgets.json"):
        super().__init__()
        self._budgets: Dict[str, Budget] = {}
        self._path = path
        self._load()

    def save_budget(self, budget: Budget) -> None:
        self._budgets[budget.name] = budget
        self._save()

    def get_budgets(self) -> List[Budget]:
        return list(self._budgets.values())

    def get_budget(self, name: str) -> Budget:
        return self._budgets[name]

    def _load(self):
        try:
            with open(appdata.from_app_data_dir(self._path), 'r') as f:
                d = json.loads(f.read())
                for b in d:
                    budget = Budget.from_dict(b)
                    self._budgets[budget.name] = budget
        except (FileNotFoundError, JSONDecodeError) as e:
            pass

    def _save(self):
        r = []
        for b in self._budgets.values():
            r.append(b.to_dict())
        with open(appdata.from_app_data_dir(self._path), "w") as f:
            f.write(json.dumps(r, indent=4))
