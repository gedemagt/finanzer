from functools import partial

from PySide6 import QtWidgets
from PySide6.QtWidgets import QTableWidget, QPushButton

from finance.gui.widgets.entry_prop_table_item import ProppedTableWidget
from finance.model.entry import Budget, Transfer

headers = ["Navn", "Betaling", "Fra", "Til"]


class TransferTableWidget(QtWidgets.QWidget):

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
        for t in self.budget.transfers:
            row = self.draw_transfer(t, row)

        btn = QPushButton("New..")
        btn.setMaximumWidth(50)
        self.table.setSpan(row, 0, 1, len(headers))
        self.table.setCellWidget(row, 0, btn)
        btn.clicked.connect(partial(self.add_new))

    def draw_transfer(self, t: Transfer, row) -> int:

        self.table.setItem(row, 0, ProppedTableWidget(t, "name"))
        self.table.setItem(row, 1, ProppedTableWidget(t, "amount"))
        self.table.setItem(row, 2, ProppedTableWidget(t, "source"))
        self.table.setItem(row, 3, ProppedTableWidget(t, "destination"))

        row += 1
        return row

    def add_new(self):
        self.budget.transfers.append(Transfer("New transfer", "", "", 0.0))
        self.redraw()
