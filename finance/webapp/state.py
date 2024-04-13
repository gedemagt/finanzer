import os
from pathlib import Path
from uuid import uuid4

from finance.model.entry import Budget


class BudgetNotFoundError(Exception):
    pass


class BudgetRepository:

    def __init__(self, parent_directory: str | Path):
        self.budgets = {}
        self.parent_directory = Path(parent_directory)
        self._load_directory()

    def _load_directory(self):
        self.budgets = {}
        if not self.parent_directory.exists():
            self.parent_directory.mkdir()
        for file in self.parent_directory.iterdir():
            if file.suffix == ".json":
                budget = Budget.load(str(file))
                self.budgets[budget.id] = budget

    def save_budget(self, budget: Budget):
        budget.save(self.parent_directory / f"{budget.id}.json")

    def create_budget(self, name: str) -> Budget:
        budget = Budget(name, id=str(uuid4()))
        self.budgets[budget.id] = budget
        self.save_budget(budget)
        return budget

    def delete_budget(self, idx: str):
        if idx in self.budgets:
            self.budgets.pop(idx)

    def get_budget(self, idx: str):
        try:
            return self.budgets[idx]
        except KeyError:
            raise BudgetNotFoundError()

    def get_budget_path(self, idx: str):
        return self.parent_directory / f"{idx}.json"


repo = BudgetRepository(os.getenv("BUDGET_DIRECTORY", "budgets"))
