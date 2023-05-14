from functools import partial

from PySide6 import QtWidgets
from PySide6.QtWidgets import QTableWidget, QPushButton, QMenu

from finance.gui.widgets.entry_prop_table_item import ProppedTableWidget
from finance.gui.widgets.helpers import create_account_combobox
from finance.model.entry import Budget, Transfer

headers = ["Navn", "Ejer", "Betaling", "Fra", "Til"]


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

        self._entry_row_mapping = {}

        self.redraw()
        self.budget.register_on_update(lambda *args: self.redraw())

    def redraw(self):
        self.table.clearContents()
        self.table.clearSpans()
        self._entry_row_mapping.clear()

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

    def contextMenuEvent(self, event):
        if self.table.selectionModel().selection().indexes():
            for i in self.table.selectionModel().selection().indexes():
                row, column = i.row(), i.column()
            menu = QMenu()
            delete = menu.addAction("Delete")
            action = menu.exec_(self.mapToGlobal(event.pos()))

            if action == delete:
                self.budget.delete(self._entry_row_mapping[row])

    def draw_transfer(self, t: Transfer, row) -> int:

        self.table.setItem(row, 0, ProppedTableWidget(t, "name"))
        self.table.setItem(row, 1, ProppedTableWidget(t, "owner"))
        self.table.setItem(row, 2, ProppedTableWidget(t, "amount"))
        self.table.setCellWidget(row, 3, create_account_combobox(t, "source", [x.name for x in self.budget.accounts]))
        self.table.setCellWidget(row, 4, create_account_combobox(t, "destination", [x.name for x in self.budget.accounts]))

        self._entry_row_mapping[row] = t

        row += 1
        return row

    def add_new(self):
        self.budget.transfers.append(Transfer("New transfer", "", "", 0.0))
        self.redraw()
