from functools import partial
from typing import List

from PySide6 import QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton
from appdata import appdata

from finance.gui.widgets.entry_prop_table_item import ProppedTableWidget
from finance.gui.widgets.group_table_item import GroupTableWidget
from finance.gui.widgets.helpers import group_header_item, create_header_font, create_month_combobox, \
    create_period_combobox, create_payment_combobox
from finance.model.entry import Budget, Entry, EntryGroup


class TableWidget(QtWidgets.QWidget):

    def __init__(self, headers: list, prefix: str, entry_group: List[EntryGroup], budget: Budget, color: QColor):
        super().__init__()

        self._prefix = prefix
        self._headers = headers
        self._entry_group = entry_group
        self._color = color

        self._group_rows_mapping = {}

        self._group_rows_mapping = {}

        self.layout = QtWidgets.QVBoxLayout(self)

        self.table = QTableWidget(0, len(self._headers))
        self.table.setHorizontalHeaderLabels(self._headers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)

        try:
            for idx, width in enumerate(appdata[f"{self._prefix}.columns"]):
                self.table.setColumnWidth(idx, width)
        except KeyError:
            pass

        self.table.itemClicked.connect(self.collapse)
        self.table.horizontalHeader().sectionResized.connect(self._save_column_size)
        self.table.itemChanged.connect(self.update_payment_size)
        self.layout.addWidget(self.table)

        self.redraw()
        budget.register_on_update(lambda *args: self.redraw())

    def _save_column_size(self, *args):
        widths = [self.table.columnWidth(i) for i in range(self.table.columnCount())]
        appdata[f"{self._prefix}.columns"] = widths

    def _set_group_hidden(self, group_name: str, hidden: bool):
        start, entries = self._group_rows_mapping[group_name]

        for x in range(start, start + entries):
            if hidden:
                self.table.hideRow(x)
            else:
                self.table.showRow(x)

    def _is_hidden(self, group_name: str):
        start, _ = self._group_rows_mapping[group_name]
        return self.table.isRowHidden(start)

    def collapse(self, k):
        if isinstance(k, GroupTableWidget):
            try:
                is_hidden = self._is_hidden(k.old_name)
                old = appdata.get(f"{self._prefix}.layout", {})
                old[k.old_name] = "visible" if is_hidden else "hidden"
                appdata[f"{self._prefix}.layout"] = old
                self._set_group_hidden(k.old_name, not is_hidden)
            except KeyError:
                pass

    def redraw(self):
        self.table.clearContents()
        self.table.clearSpans()

        total_rows = sum(2 + len(x.entries) for x in self._entry_group) + 1

        self.table.setRowCount(total_rows)

        row = 0
        for g in self._entry_group:
            row = self.draw_group(g, row)
        self.add_new_group_row(row)

        for group in self._entry_group:
            try:
                if appdata[f"{self._prefix}.layout"][group.name] == "hidden":
                    self._set_group_hidden(group.name, True)
            except KeyError:
                pass

    def draw_group(self, group: EntryGroup, start_row) -> int:
        row = start_row
        self.table.setSpan(row, 0, 1, len(self._headers) - 1)
        self.table.setItem(row, 0, group_header_item(group.name, self._color))

        self._group_rows_mapping[group.name] = (row + 1, len(group.entries) + 1)

        row += 1

        monthly_sum = 0.0

        for e in group.entries:
            monthly_widget = QTableWidgetItem(f"{e.monthly():0.2f}")
            monthly_widget.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            monthly_widget.setFlags(~Qt.ItemIsEditable)

            self.table.setItem(row, 0, ProppedTableWidget(e, "name"))
            self.table.setItem(row, 1, ProppedTableWidget(e, "owner"))
            self.table.setItem(row, 2, ProppedTableWidget(e, "payment_size"))
            self.table.setCellWidget(row, 3, create_period_combobox(e, "payment_period"))
            if e.payment_period > 1:
                self.table.setCellWidget(row, 4, create_month_combobox(e, "first_payment_month"))
            self.table.setCellWidget(row, 5, create_payment_combobox(e, "payment_method"))
            self.table.setItem(row, 6, ProppedTableWidget(e, "account"))
            self.table.setItem(row, 7, monthly_widget)
            row += 1
            monthly_sum += e.monthly()

        sum_r_widget = QTableWidgetItem(f"{monthly_sum:0.2f}")
        sum_r_widget.setBackground(self._color)
        sum_r_widget.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
        sum_r_widget.setFlags(~Qt.ItemIsEditable)
        sum_r_widget.setFont(create_header_font())
        self.table.setItem(row - len(group.entries) - 1, len(self._headers) - 1, sum_r_widget)

        btn = QPushButton("New..")
        btn.setMaximumWidth(50)
        self.table.setSpan(row, 0, 1, 7)
        self.table.setCellWidget(row, 0, btn)
        btn.clicked.connect(partial(self.add_new, group))
        row += 1

        return row

    def add_new_group_row(self, row):
        btn = QPushButton("New group..")
        btn.setMaximumWidth(150)
        self.table.setSpan(row, 0, 1, 6)
        self.table.setCellWidget(row, 0, btn)
        btn.clicked.connect(self.add_new_group)

    def add_new_group(self):
        self._entry_group.append(EntryGroup("New group"))
        self.redraw()

    def add_new(self, group):
        group.entries.append(Entry("New item", 0.0))
        self.redraw()

    def update_payment_size(self, k):
        if isinstance(k, GroupTableWidget):
            for e in self._entry_group:
                if e.name == k.old_name and e.name != k.text():
                    e.name = k.text()
            k.old_name = k.text()
