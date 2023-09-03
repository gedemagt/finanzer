from collections import defaultdict
from typing import Dict, List

from finance.model.entry import Budget, Entry
import numpy as np


MONTHS = [
    "Januar", "Februar", "Marts", "April", "Maj", "Juni",
    "Juli", "August", "September", "Oktober", "November", "December"
]

PAYMENT_METHODS = ["BS", "Kort", "MobilePay", "Overførsel"]

PERIODS = {
    "Månedvis": 1,
    "Kvartalsvis": 3,
    "Halvårlig": 6,
    "Årlig": 12
}


def monthly(budget: Budget, account: str):
    monthly_expenses = np.zeros(12)
    monthly_incomes = np.zeros(12)

    for e in [_e for _e in budget.all_expenses() if _e.account == account]:

        for m in e.pay_months():
            monthly_expenses[m-1] += (e.payment_size + e.payment_fee)

    for t in budget.transfers:
        if t.source == account:
            monthly_expenses += t.amount
        elif t.destination == account:
            monthly_incomes += t.amount

    return monthly_expenses, monthly_incomes


def expected_saldo(monthly_expenses):

    n = len(monthly_expenses)

    saldo = np.zeros(n)
    avg_expense = np.average(monthly_expenses)

    pivot = np.argmax(monthly_expenses)

    for x in range(n):
        idx = (x + pivot) % n
        if monthly_expenses[(x + pivot) % n] < avg_expense:
            break
        else:
            pivot = idx

    for i in range(1, n):
        idx = (i + pivot) % n
        saldo[idx] = saldo[idx - 1] - monthly_expenses[idx] + avg_expense

    return saldo


def get_monthly_movements(budget: Budget, account: str, months=None) -> Dict[int, List[Entry]]:
    if months is None:
        months = list(range(1, 13))

    groups = defaultdict(list)

    for entry in budget.all_expenses():
        if entry.account == account:
            for m in entry.pay_months():
                if entry.payment_size > 0 and m in months:
                    groups[m].append(entry)

    return groups
