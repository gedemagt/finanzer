import logging
import sys

from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtWidgets import QVBoxLayout, QTabWidget, QWidget, QHBoxLayout, QMainWindow, QApplication, QFileDialog
from appdata import appdata

from finance.gui.widgets.account_activity import AccountWidget
from finance.gui.widgets.expenses import ExpenseTableWidget

from finance.gui.widgets.incomes import IncomeTableWidget
from finance.gui.widgets.pie_chart import TestChart
from finance.gui.widgets.toolbar import Toolbar
from finance.gui.widgets.transfers import TransferTableWidget
from finance.model.entry import Budget


def build_layout(budget: Budget) -> QWidget:
    layout = QHBoxLayout()

    right_layout = QVBoxLayout()
    right_layout.addWidget(AccountWidget(budget), 2)
    right_layout.addWidget(TestChart(budget), 2)

    left_layout = QVBoxLayout()
    tabs = QTabWidget()
    tabs.addTab(ExpenseTableWidget(budget), "Expenses")
    tabs.addTab(IncomeTableWidget(budget), "Incomes")
    tabs.addTab(TransferTableWidget(budget), "Transfers")
    left_layout.addWidget(tabs)

    layout.addLayout(left_layout, 12)
    layout.addLayout(right_layout, 8)
    widget = QWidget()
    widget.setLayout(layout)

    return widget


class Application(QApplication):

    def __init__(self):
        super().__init__()

        self._budget = None

        self.window = QMainWindow()
        self.window.showMaximized()

        shortcut = QShortcut(QKeySequence("Ctrl+S"), self.window)
        shortcut.activated.connect(self._save_budget)

        self._toolbar = Toolbar()
        self._toolbar.set_on_load(lambda x: self.set_budget(Budget.load(x)))
        self._toolbar.set_on_new(lambda: self.set_budget(Budget("My Budget")))

        self.window.addToolBar(self._toolbar)
        self.window.show()

        try:
            budget = Budget.load(appdata["last_budget"])
            self.set_budget(budget)
        except KeyError:
            budget = Budget("My Budget")
            self.set_budget(budget)

    def set_budget(self, budget: Budget):
        self._budget = budget
        self.window.setWindowTitle(f"Budget: {budget.name}")
        self.window.setCentralWidget(build_layout(budget))

        if budget.path:
            appdata["last_budget"] = budget.path

    def _save_budget(self):
        if not self._budget.path:
            f_name, _filter = QFileDialog.getSaveFileName(self.window, filter="*.json")
            self._budget.path = f_name
        self._budget.save()


if __name__ == "__main__":

    logging.basicConfig(level="INFO")

    app = Application()

    sys.exit(app.exec())
