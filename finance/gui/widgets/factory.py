from PySide6.QtGui import QColor

from finance.gui.widgets.table import TableWidget
from finance.model.entry import Budget


def create_expense_table(budget: Budget) -> TableWidget:
    return TableWidget(
        ["Navn", "Ejer", "Beløb", "Frekvens", "Første forfald", "Betalingsmåde", "Konto", "Månedligt"],
        "expenses",
        budget.expenses,
        budget,
        QColor.fromRgb(191, 82, 75, 255)
    )


def create_income_table(budget: Budget) -> TableWidget:
    return TableWidget(
        ["Navn", "Ejer", "Beløb", "Konto", "Månedligt"],
        "incomes",
        budget.incomes,
        budget,
        QColor.fromRgb(75, 191, 75, 255)
    )
