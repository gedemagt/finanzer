from pathlib import Path
from uuid import uuid4

from finance.model.entry import Budget


class BudgetRepository:

    def __init__(self):
        self.budgets = []
        self.parent_directory = None
        self.selected = 0

    def set_directory(self, parent_directory: str | Path):
        self.budgets: list[Budget] = []
        self.parent_directory = Path(parent_directory)
        if not self.parent_directory.exists():
            self.parent_directory.mkdir()
        for file in self.parent_directory.iterdir():
            if file.suffix == ".json":
                self.budgets.append(Budget.load(str(file)))

    def copy_budget(self, idx: int, name: str):
        budget = Budget.from_dict(self.budgets[idx].to_dict())
        budget.name = name
        if self.parent_directory:
            budget.path = self.parent_directory / f"{name}.json"
        else:
            budget.path = None
        self.budgets.append(budget)
        return len(self.budgets) - 1

    def create_budget(self, name: str) -> int:
        budget = Budget(name, str(uuid4()))
        if self.parent_directory:
            budget.path = self.parent_directory / f"{name}.json"
        self.budgets.append(budget)
        return len(self.budgets) - 1

    def delete_budget(self, idx: int):
        self.budgets.pop(idx)

    def get_budget(self, idx: int = None):
        if idx is None:
            idx = self.selected
        return self.budgets[idx]

    def select(self, idx):
        self.selected = idx


repo = BudgetRepository()
