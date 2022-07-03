from functools import partial
from typing import Any

from PySide6 import QtWidgets, QtCore
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton, QAbstractItemView, QComboBox

from finance.model.entry import Budget, Entry, EntryGroup

headers = ["Navn", "Betalingsstørrelse", "Afgift", "Betalingsperiode", "Første årlige forfald", "Betalingsmåde", "Konto", "Tag", "Månedligt"]

MONTHS = ["Januar", "Februar", "Marts", "April", "Maj", "Juni", "Juli", "August", "September", "Oktober", "November", "December"]


class EntryPropTableWidget(QTableWidgetItem):

    def __init__(self, entry: Entry, prop: str):
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


class GroupTableWidget(QTableWidgetItem):

    def __init__(self, name):
        QTableWidgetItem.__init__(self, name)
        self.old_name = name
        self.setBackground(QColor.fromRgb(191, 82, 75, 255))


def item(entry: Entry, prop: str, editable=False, align_right=True):

    _item = EntryPropTableWidget(entry, prop)
    _item.setTextAlignment(QtCore.Qt.AlignVCenter)
    if align_right:
        _item.setTextAlignment(_item.textAlignment() | QtCore.Qt.AlignRight)


    #_item.setFlags(~QtCore.Qt.ItemIsEditable & ~QtCore.Qt.ItemIsSelectable)
    if not editable:
        _item.setFlags(~QtCore.Qt.ItemIsEditable)

    return _item


def create_header_font():
    font = QFont()
    font.setBold(True)
    return font


def group_header_item(name: str):
    group_header = GroupTableWidget(name)
    group_header.setFont(create_header_font())
    return group_header


class ExpenseTableWidget(QtWidgets.QWidget):

    def __init__(self, budget: Budget):
        super().__init__()

        self.budget = budget

        self.layout = QtWidgets.QVBoxLayout(self)

        self.table = QTableWidget(0, len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)

        self.table.itemChanged.connect(self.update_payment_size)
        self.layout.addWidget(self.table)

        # self.table.setDragDropMode(QAbstractItemView.InternalMove)
        # select one row at a time
        # self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        # self.table.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.redraw()
        self.budget.register_on_update(lambda *args: self.redraw())

    def redraw(self):
        self.table.clearContents()
        self.table.clearSpans()

        total_rows = sum(2 + len(x.entries) for x in self.budget.expenses) + 1

        self.table.setRowCount(total_rows)

        row = 0
        for g in self.budget.expenses:
            row = self.draw_group(g, row)
        self.add_new_group_row(row)

    def draw_group(self, group: EntryGroup, start_row) -> int:
        row = start_row
        self.table.setSpan(row, 0, 1, len(headers) - 1)
        self.table.setItem(row, 0, group_header_item(group.name))

        row += 1

        monthly_sum = 0.0

        for e in group.entries:

            monthly_widget = QTableWidgetItem(f"{e.monthly():0.2f}")
            monthly_widget.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)

            self.table.setItem(row, 0, item(e, "name", True, False))
            self.table.setItem(row, 1, item(e, "payment_size", True))
            self.table.setItem(row, 2, item(e, "payment_fee", True))
            # self.table.setItem(row, 3, item(e, "payment_period", True))
            self.table.setCellWidget(row, 3, self.create_period_combobox(e, "payment_period"))
            # self.table.setItem(row, 4, item(e, "first_payment_month", True))
            if e.payment_period > 1:
                self.table.setCellWidget(row, 4, self.create_month_combobox(e, "first_payment_month"))
            # self.table.setItem(row, 5, item(e, "payment_method", True, False))
            self.table.setCellWidget(row, 5, self.create_combobox(e, "payment_method"))
            self.table.setItem(row, 6, item(e, "account", True, False))
            self.table.setItem(row, 7, item(e, "tag", True, False))
            self.table.setItem(row, 8, monthly_widget)
            row += 1
            monthly_sum += e.monthly()

        sum_r_widget = QTableWidgetItem(f"{monthly_sum:0.2f}")
        sum_r_widget.setBackground(QColor.fromRgb(191, 82, 75, 255))
        sum_r_widget.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        sum_r_widget.setFont(create_header_font())
        self.table.setItem(row - len(group.entries) - 1, len(headers) - 1, sum_r_widget)

        btn = QPushButton("New..")
        btn.setMaximumWidth(50)
        self.table.setSpan(row, 0, 1, 9)
        self.table.setCellWidget(row, 0, btn)
        btn.clicked.connect(partial(self.add_new, group))
        row += 1

        return row

    def create_month_combobox(self, entry, prop):
        cb = QComboBox()
        cb.addItems(["Januar", "Februar", "Marts", "April", "Maj", "Juni", "Juli", "August", "September", "Oktober", "November", "December"])
        cb.setCurrentIndex(getattr(entry, prop)-1)

        def on_change():
            setattr(entry, prop, cb.currentIndex()+1)

        cb.currentTextChanged.connect(on_change)
        return cb

    def create_period_combobox(self, entry, prop):
        cb = QComboBox()
        m = {
            "Månedvis": 1,
            "Kvartalsvis": 3,
            "Halvårlig": 6,
            "Årlig": 12
        }
        cb.addItems(m.keys())
        cb.setCurrentIndex(list(m.values()).index(getattr(entry, prop)))

        def on_change():
            setattr(entry, prop, m[cb.currentText()])

        cb.currentTextChanged.connect(on_change)
        return cb

    def create_combobox(self, entry, prop):
        cb = QComboBox()
        cb.addItems(["BS", "Kort", "MobilePay", "Overførsel"])
        cb.setCurrentText(getattr(entry, prop))

        def on_change():
            setattr(entry, prop, cb.currentText())

        cb.currentTextChanged.connect(on_change)
        return cb

    def add_new_group_row(self, row):
        btn = QPushButton("New group..")
        btn.setMaximumWidth(150)
        self.table.setSpan(row, 0, 1, 8)
        self.table.setCellWidget(row, 0, btn)
        btn.clicked.connect(self.add_new_group)

    def add_new_group(self):
        self.budget.expenses.append(EntryGroup("New group"))
        self.redraw()

    def add_new(self, group):
        group.entries.append(Entry("New item", 0.0))
        self.redraw()

    def update_payment_size(self, k):
        if isinstance(k, GroupTableWidget):
            for e in self.budget.expenses:
                if e.name == k.old_name and e.name != k.text():
                    e.name = k.text()
            k.old_name = k.text()
