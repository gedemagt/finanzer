from functools import partial

from PySide6 import QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton

from finance.gui.widgets.entry_prop_table_item import ProppedTableWidget
from finance.gui.widgets.group_table_item import GroupTableWidget
from finance.gui.widgets.helpers import group_header_item, create_header_font, create_month_combobox, \
    create_period_combobox, create_payment_combobox
from finance.model.entry import Budget, Entry, EntryGroup

HEADERS = ["Navn", "Beløb", "Frekvens", "Første forfald", "Betalingsmåde", "Konto", "Månedligt"]


COLOR = QColor.fromRgb(191, 82, 75, 255)


class ExpenseTableWidget(QtWidgets.QWidget):

    def __init__(self, budget: Budget):
        super().__init__()

        self.budget = budget

        self.layout = QtWidgets.QVBoxLayout(self)

        self.table = QTableWidget(0, len(HEADERS))
        self.table.setHorizontalHeaderLabels(HEADERS)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)

        self.table.itemChanged.connect(self.update_payment_size)
        self.layout.addWidget(self.table)

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
        self.table.setSpan(row, 0, 1, len(HEADERS) - 1)
        self.table.setItem(row, 0, group_header_item(group.name, COLOR))

        row += 1

        monthly_sum = 0.0

        for e in group.entries:

            monthly_widget = QTableWidgetItem(f"{e.monthly():0.2f}")
            monthly_widget.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            monthly_widget.setFlags(~Qt.ItemIsEditable)

            self.table.setItem(row, 0, ProppedTableWidget(e, "name"))
            self.table.setItem(row, 1, ProppedTableWidget(e, "payment_size"))
            self.table.setCellWidget(row, 2, create_period_combobox(e, "payment_period"))
            if e.payment_period > 1:
                self.table.setCellWidget(row, 3, create_month_combobox(e, "first_payment_month"))
            self.table.setCellWidget(row, 4, create_payment_combobox(e, "payment_method"))
            self.table.setItem(row, 5, ProppedTableWidget(e, "account"))
            self.table.setItem(row, 6, monthly_widget)
            row += 1
            monthly_sum += e.monthly()

        sum_r_widget = QTableWidgetItem(f"{monthly_sum:0.2f}")
        sum_r_widget.setBackground(COLOR)
        sum_r_widget.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
        sum_r_widget.setFlags(~Qt.ItemIsEditable)
        sum_r_widget.setFont(create_header_font())
        self.table.setItem(row - len(group.entries) - 1, len(HEADERS) - 1, sum_r_widget)

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
