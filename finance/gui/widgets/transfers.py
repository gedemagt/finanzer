from functools import partial
from typing import Any

from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton

from finance.model.entry import Budget, Transfer

headers = ["Navn", "Betaling", "Fra", "Til"]


class TransferPropTableWidget(QTableWidgetItem):

    def __init__(self, entry: Transfer, prop: str):
        self.entry = entry
        self.prop = prop
        self.type = entry.__annotations__[prop]

        val = getattr(self.entry, prop)
        if isinstance(val, float):
            val = f"{val:0.2f}"
        else:
            val = str(val)

        QTableWidgetItem.__init__(self, val)

    def value(self):
        return getattr(self.entry, self.prop)

    def setData(self, role: int, value: Any) -> None:
        if role == 2:
            try:
                converted = self.type(value)
                super().setData(role, converted)
                setattr(self.entry, self.prop, converted)
            except ValueError:
                pass
        else:
            super().setData(role, value)


def item(entry: Transfer, prop: str, editable=False, align_right=True):

    _item = TransferPropTableWidget(entry, prop)
    _item.setTextAlignment(QtCore.Qt.AlignVCenter)
    if align_right:
        _item.setTextAlignment(_item.textAlignment() | QtCore.Qt.AlignRight)


    #_item.setFlags(~QtCore.Qt.ItemIsEditable & ~QtCore.Qt.ItemIsSelectable)
    if not editable:
        _item.setFlags(~QtCore.Qt.ItemIsEditable)

    return _item


class TransferTableWidget(QtWidgets.QWidget):

    def __init__(self, budget: Budget):
        super().__init__()

        self.budget = budget

        self.layout = QtWidgets.QVBoxLayout(self)

        self.table = QTableWidget(0, len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)

        # self.table.itemChanged.connect(self.update_payment_size)
        self.layout.addWidget(self.table)

        self.redraw()

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

        self.table.setItem(row, 0, item(t, "name", True, False))
        self.table.setItem(row, 1, item(t, "amount", True))
        self.table.setItem(row, 2, item(t, "source", True))
        self.table.setItem(row, 3, item(t, "destination", True))

        row += 1
        return row

    def add_new(self):
        self.budget.transfers.append(Transfer("New transfer", "", "", 0.0))
        self.redraw()
    #
    # def update_payment_size(self, k):
    #     if isinstance(k, GroupTableWidget):
    #         for e in self.budget.expenses:
    #             if e.name == k.old_name:
    #                 e.name = k.text()
    #         k.old_name = k.text()
