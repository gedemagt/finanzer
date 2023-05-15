from functools import partial

from PySide6 import QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidget, QPushButton, QTableWidgetItem

from finance.gui.widgets.entry_prop_table_item import ProppedTableWidget
from finance.gui.widgets.helpers import create_enum_combobox
from finance.model.entry import Budget, Account, AccountType

headers = ["Navn", "Ejer", "Type", "Før udgifter", "Efter udgifter"]


class AccountTableWidget(QtWidgets.QWidget):

    def __init__(self, budget: Budget):
        super().__init__()

        self.budget = budget

        self.layout = QtWidgets.QVBoxLayout(self)

        self.table = QTableWidget(0, len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)

        self.layout.addWidget(self.table)

        self.redraw()
        self.budget.register_on_update(lambda *args: self.redraw())

    def redraw(self):
        self.table.clearContents()
        self.table.clearSpans()

        total_rows = len(self.budget.transfers) + 1
        self.table.setRowCount(total_rows)

        row = 0
        for t in self.budget.accounts:
            row = self.draw_account(t, row)

        btn = QPushButton("New..")
        btn.setMaximumWidth(50)
        self.table.setSpan(row, 0, 1, len(headers))
        self.table.setCellWidget(row, 0, btn)
        btn.clicked.connect(partial(self.add_new))

    def draw_account(self, t: Account, row) -> int:
        expense_balances, income_balances, transfer_balances = self.budget.calculate_balances()

        before = income_balances[t.name] + transfer_balances[t.name]

        balance_before_widget = QTableWidgetItem(f"{before:0.2f}")
        balance_before_widget.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
        balance_before_widget.setFlags(~Qt.ItemIsEditable)

        balance_after_widget = QTableWidgetItem(f"{before + expense_balances[t.name]:0.2f}")
        balance_after_widget.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
        balance_after_widget.setFlags(~Qt.ItemIsEditable)

        self.table.setItem(row, 0, ProppedTableWidget(t, "name"))
        self.table.setItem(row, 1, ProppedTableWidget(t, "owner"))
        self.table.setCellWidget(row, 2, create_enum_combobox(t, "type", AccountType))
        self.table.setItem(row, 3, balance_before_widget)
        self.table.setItem(row, 4, balance_after_widget)

        row += 1
        return row

    def add_new(self):
        self.budget.accounts.append(Account("Ny konto", "", False))
        self.redraw()
