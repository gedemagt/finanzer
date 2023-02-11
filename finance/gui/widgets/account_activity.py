from datetime import datetime

from PySide6 import QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QComboBox, QTabWidget, QLabel

from appdata import appdata

from finance.gui.widgets.helpers import MONTHS
from finance.model.entry import Budget
from finance.utils.monthly_overview import monthly, expected_saldo, get_monthly_movements


def item(val):
    if isinstance(val, float):
        val = f"{val:0.2f}"
    else:
        val = str(val)
    _item = QTableWidgetItem(val)
    _item.setTextAlignment(Qt.AlignRight)
    return _item


class MonthlyMovements(QtWidgets.QWidget):

    def __init__(self, budget: Budget, block_size=3):
        super().__init__()

        self.budget = budget
        self._block_size = block_size

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layer = QtWidgets.QHBoxLayout(self)

        self.combo_box = QComboBox()
        self.combo_box.addItems(
            [f"{MONTHS[start]}-{MONTHS[start + self._block_size - 1]}" for start in range(0, 12, self._block_size)]
        )

        self._list_widgets = []
        self._labels = []

        self._block = datetime.now().month // self._block_size
        self.combo_box.setCurrentIndex(self._block)

        for _ in range(self._block_size):
            table = QTableWidget(0, 2)
            table.verticalHeader().setVisible(False)
            table.horizontalHeader().setVisible(False)

            label = QLabel("")
            layer = QtWidgets.QVBoxLayout()
            self._labels.append(label)

            self._list_widgets.append(table)
            layer.addWidget(label)
            layer.addWidget(table)
            self.layer.addLayout(layer)

        self.layout.addWidget(self.combo_box)
        self.layout.addLayout(self.layer)

        self._account = None

        self.budget.register_on_update(lambda *args: self.draw_account(self._account))
        self.combo_box.currentIndexChanged.connect(self.selectionchange)

    def selectionchange(self, i):
        self._block = i
        self.draw_account(self._account)

    def draw_account(self, account: str):
        self._account = account

        start = self._block * self._block_size
        end = start + self._block_size
        groups = get_monthly_movements(self.budget, self._account, range(start, end+1))

        for idx, month in enumerate(MONTHS[start:end]):
            list_widget = self._list_widgets[idx]
            self._labels[idx].setText(month)

            list_widget.clearContents()
            list_widget.clearSpans()

            entries = groups[idx + start]
            list_widget.setRowCount(len(entries) + 1)
            total = 0
            for row, entry in enumerate(sorted(entries, key=lambda e: e.payment_period)):
                list_widget.setItem(row, 0, QTableWidgetItem(f"{entry.name}"))
                list_widget.setItem(row, 1, item(f"{entry.payment_size}"))
                total += entry.payment_size

            list_widget.setItem(len(entries), 0, QTableWidgetItem(f"Total"))
            list_widget.setItem(len(entries), 1, item(f"{total}"))


class AccountWidget(QtWidgets.QWidget):

    def __init__(self, budget: Budget):
        super().__init__()

        self.budget = budget

        self.tabs = QTabWidget()

        self.layout = QtWidgets.QVBoxLayout(self)

        self.combo_box = QComboBox()
        self.combo_box.addItems(self.budget.budget_accounts)

        self.combo_box.setCurrentText(appdata.get("selected_budget", None))

        self.combo_box.currentIndexChanged.connect(self.selectionchange)
        self.layout.addWidget(self.combo_box)

        self.table = QTableWidget(13, 4)
        self.table.setHorizontalHeaderLabels(["", "Udgift", "Incomes", "Saldo"])
        # self.table.setVerticalHeaderLabels(MONTHS)
        self.table.verticalHeader().setVisible(False)

        self._movements = MonthlyMovements(self.budget)

        self.tabs.addTab(self.table, "Saldo")
        self.tabs.addTab(self._movements, "Movements")

        self.layout.addWidget(self.tabs)

        self.draw_account(self.combo_box.currentText())
        self._movements.draw_account(self.combo_box.currentText())
        self.budget.register_on_update(lambda *args: self.draw_account(self.combo_box.currentText()))

    def selectionchange(self, i):
        appdata["selected_budget"] = self.combo_box.currentText()
        self.draw_account(self.combo_box.currentText())
        self._movements.draw_account(self.combo_box.currentText())

    def draw_account(self, account: str):

        monthly_expenses, monthly_incomes = monthly(self.budget, account)

        average_expense = sum(monthly_expenses) / 12
        average_income = sum(monthly_incomes) / 12

        diff = sum(monthly_incomes) - sum(monthly_expenses)

        self.table.setItem(0, 0, item("Gennemsnit"))
        self.table.setItem(0, 1, item(average_expense))
        self.table.setItem(0, 2, item(average_income))
        self.table.setItem(0, 3, item(diff))

        saldos = expected_saldo(monthly_expenses, monthly_incomes)

        for row, (m, e, i, s) in enumerate(zip(MONTHS, monthly_expenses, monthly_incomes, saldos)):
            self.table.setItem(row + 1, 0, item(m))
            self.table.setItem(row + 1, 1, item(e))
            self.table.setItem(row + 1, 2, item(i))
            self.table.setItem(row + 1, 3, item(s))
