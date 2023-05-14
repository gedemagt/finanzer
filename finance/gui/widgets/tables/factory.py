from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem

from finance.gui.color_map import EXPENSE_COLOR, INCOME_COLOR
from finance.gui.widgets.entry_prop_table_item import ProppedTableWidget
from finance.gui.widgets.helpers import create_month_combobox, \
    create_period_combobox, create_payment_combobox, create_account_combobox
from finance.gui.widgets.tables.table import TableWidget
from finance.model.entry import Budget, Entry


class ExpenseTable(TableWidget):

    def __init__(self, budget: Budget):
        super().__init__(
            ["Navn", "Ejer", "Beløb", "Frekvens", "Første forfald", "Betalingsmåde", "Konto", "Månedligt"],
            "expenses",
            budget.expenses,
            budget,
            EXPENSE_COLOR
        )

    def draw_entries(self, e: Entry, table: QTableWidget, row, budget: Budget):
        monthly_widget = QTableWidgetItem(f"{e.monthly():0.2f}")
        monthly_widget.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
        monthly_widget.setFlags(~Qt.ItemIsEditable)

        table.setItem(row, 0, ProppedTableWidget(e, "name"))
        table.setItem(row, 1, ProppedTableWidget(e, "owner"))
        table.setItem(row, 2, ProppedTableWidget(e, "payment_size"))
        table.setCellWidget(row, 3, create_period_combobox(e, "payment_period"))
        if e.payment_period > 1:
            table.setCellWidget(row, 4, create_month_combobox(e, "first_payment_month"))
        table.setCellWidget(row, 5, create_payment_combobox(e, "payment_method"))
        table.setCellWidget(row, 6, create_account_combobox(e, "account", [x.name for x in budget.accounts]))
        table.setItem(row, 7, monthly_widget)


class IncomeTable(TableWidget):

    def __init__(self, budget: Budget):
        super().__init__(
            ["Navn", "Ejer", "Beløb", "Konto", "Månedligt"],
            "incomes",
            budget.incomes,
            budget,
            INCOME_COLOR
        )

    def draw_entries(self, e: Entry, table: QTableWidget, row, budget: Budget):
        monthly_widget = QTableWidgetItem(f"{e.monthly():0.2f}")
        monthly_widget.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
        monthly_widget.setFlags(~Qt.ItemIsEditable)

        table.setItem(row, 0, ProppedTableWidget(e, "name"))
        table.setItem(row, 1, ProppedTableWidget(e, "owner"))
        table.setItem(row, 2, ProppedTableWidget(e, "payment_size"))
        table.setCellWidget(row, 3, create_account_combobox(e, "account", [x.name for x in budget.accounts]))
        table.setItem(row, 4, monthly_widget)


def create_expense_table(budget: Budget) -> TableWidget:
    return ExpenseTable(budget)


def create_income_table(budget: Budget) -> TableWidget:
    return IncomeTable(budget)
