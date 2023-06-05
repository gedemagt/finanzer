from appdata import appdata

from finance.model.entry import Budget

budgets = []

try:
    budgets.append(Budget.load(appdata["last_budget"]))
except (KeyError, FileNotFoundError):
    budgets.append(Budget("My Budget"))


def set_budget(idx: int):
    _state[0] = budgets[idx]


_state = [budgets[0]]


def get_budget(idx=0):
    return _state[0]
