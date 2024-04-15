import dataclasses
import json
import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Union, Any, Dict
from uuid import uuid4


class Observable:

    def __init__(self):
        self._on_update_listeners = []

    def register_on_update(self, callback):
        self._on_update_listeners.append(callback)

    def notify(self, name, value):
        for listener in self._on_update_listeners:
            listener(self, name, value)

    def __post_init__(self):
        setattr(self, "_on_update_listeners", [])

        def method(self, name, value):
            super(self.__class__, self).__setattr__(name, value)
            self.notify(name, value)

        meths = {'__setattr__': method}
        self.__class__ = type('Observable', (self.__class__,), meths)


class AccountType(str, Enum):

    Spending = "Forbrug"
    Savings = "Opsparing"
    Income = "Lønkonto"
    Budget = "Budget"


@dataclass
class Account(Observable):

    name: str
    owner: str
    type: AccountType
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass
class Entry(Observable):

    name: str
    payment_size: float
    payment_period: int = 1
    first_payment_month: int = 1
    payment_fee: float = 0.0
    payment_method: str = ""
    account: str = ""
    tag: str = ""
    owner: str = ""
    id: str = field(default_factory=lambda: str(uuid4()))

    def monthly(self):
        return (self.payment_size + self.payment_fee) / self.payment_period

    def pay_months(self):
        """
        Returns a list of months in which the entry is paid. It is month numbers i.e. January is 1, February is 2 etc.
        :return:
        """
        return sorted(
            (self.first_payment_month - 1 + x * self.payment_period) % 12 + 1 for x in range(12 // self.payment_period)
        )


@dataclass
class EntryGroup(Observable):
    name: str
    entries: List[Entry] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid4()))

    def add_entry(self, entry: Entry):
        self.entries.append(entry)
        entry.register_on_update(lambda x, y, z: self.notify("entries", self.entries))
        self.notify("entries", self.entries)

    def delete_entry(self, entry: Entry):
        if entry in self.entries:
            self.entries.remove(entry)
            self.notify("entries", self.entries)
            return True
        return False

    def total_monthly(self):
        return sum(x.monthly() for x in self.entries)


@dataclass
class Transfer(Observable):

    name: str
    source: str
    destination: str
    amount: float
    owner: str = ""
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass
class Budget(Observable):

    name: str
    expenses: List[EntryGroup] = field(default_factory=list)
    incomes: List[EntryGroup] = field(default_factory=list)
    transfers: List[Transfer] = field(default_factory=list)
    budget_accounts: List[str] = field(default_factory=list)
    accounts: List[Account] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid4()))
    extra: Dict[str, Any] = field(default_factory=dict)

    def copy(self):
        budget = Budget.from_dict(self.to_dict())
        budget.id = str(uuid4())
        return budget

    def total_monthly(self):
        return sum(x.total_monthly() for x in self.expenses)

    def total_monthly_income(self):
        return sum(x.total_monthly() for x in self.incomes)

    def all_expenses(self) -> List[Entry]:
        result = []
        for exp in self.expenses:
            result += exp.entries

        return result

    def expense_grp_from_id(self, _id: str):
        return next(x for x in self.expenses if x.id == _id)

    def income_grp_from_id(self, _id: str):
        return next(x for x in self.incomes if x.id == _id)

    def add_expense_group(self, entry_group: EntryGroup):
        entry_group.register_on_update(lambda x, y, z: self.notify("expenses", self.expenses))
        self.expenses.append(entry_group)

    def add_incomes_group(self, entry_group: EntryGroup):
        entry_group.register_on_update(lambda x, y, z: self.notify("incomes", self.incomes))
        self.incomes.append(entry_group)

    def add_transfer(self, transfer: Transfer):
        transfer.register_on_update(lambda x,y,z: self.notify("transfers", self.transfers))
        self.transfers.append(transfer)

    def all_incomes(self):
        result = []
        for inc in self.incomes:
            result += inc.entries
        return result

    def save(self, path: str | Path):
        logging.info(f"Saving budget to {path}")
        with open(path, "w+") as f:
            f.write(json.dumps(self.to_dict(), indent=4, ensure_ascii=False))

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)

    def add_extra(self, key, value):
        self.extra[key] = value

    @staticmethod
    def from_dict(data: dict):
        b = Budget(data["name"], id=data["id"])
        for e_grp in data["expenses"]:
            grp = EntryGroup(e_grp["name"], id=e_grp.get("id", str(uuid4())))

            for e in e_grp["entries"]:
                grp.add_entry(Entry(**e))
            b.add_expense_group(grp)

        for e_grp in data["incomes"]:
            grp = EntryGroup(e_grp["name"], id=e_grp.get("id", str(uuid4())))
            for e in e_grp["entries"]:
                grp.add_entry(Entry(**e))
            b.add_incomes_group(grp)

        for t in data["transfers"]:
            b.add_transfer(Transfer(**t))

        for b_acc in data["budget_accounts"]:
            b.budget_accounts.append(b_acc)

        for acc in data["accounts"]:
            b.accounts.append(Account(**acc))

        b.extra = data.get("extra", {})

        return b

    @staticmethod
    def load(path: str):
        with open(path, "r") as f:
            data = json.loads(f.read())
            b = Budget.from_dict(data)
            b.path = os.path.abspath(path)
            return b

    def delete(self, entry: Union[Entry, Transfer]):
        if isinstance(entry, Entry):
            for x in self.incomes + self.expenses:
                if x.delete_entry(entry):
                    break
        elif isinstance(entry, Transfer):
            if entry in self.transfers:
                self.transfers.remove(entry)
                self.notify("transfers", self.transfers)

    def calculate_balances(self):
        expense_result = {x.name: 0 for x in self.accounts}
        income_result = {x.name: 0 for x in self.accounts}
        transfer_result = {x.name: 0 for x in self.accounts}
        for x in self.expenses:
            for e in x.entries:
                try:
                    expense_result[e.account] -= e.monthly()
                except KeyError as exc:
                    logging.error(f"Could not find expense_result for {e.account}", exc_info=exc)

        for x in self.incomes:
            for e in x.entries:
                try:
                    income_result[e.account] += e.monthly()
                except KeyError as exc:
                    logging.error(f"Could not find income_result for {e.account}", exc_info=exc)

        for x in self.transfers:
            try:
                transfer_result[x.source] -= x.amount
            except KeyError as exc:
                logging.error(f"Could not find transfer_result for {x.source}", exc_info=exc)
            try:
                transfer_result[x.destination] += x.amount
            except KeyError as exc:
                logging.error(f"Could not find transfer_result for {x.destination}", exc_info=exc)

        return expense_result, income_result, transfer_result
