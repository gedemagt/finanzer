import sys

from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtWidgets import QVBoxLayout, QTabWidget, QWidget, QHBoxLayout, QMainWindow, QApplication

from appdata import from_app_data_dir
from finance.gui.widgets.account_activity import AccountWidget
from finance.gui.widgets.expenses import ExpenseTableWidget
from qt_material import apply_stylesheet

from finance.gui.widgets.incomes import IncomeTableWidget
from finance.gui.widgets.pie_chart import TestChart
from finance.gui.widgets.transfers import TransferTableWidget
from finance.model.entry import Budget
from finance.repository.budget_repo import DocumentRepo


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

    layout.addLayout(left_layout, 1)
    layout.addLayout(right_layout, 1)
    widget = QWidget()
    widget.setLayout(layout)
    return widget


if __name__ == "__main__":

    #appdata.set_app_dir_provider(AppDirsProvider(AppDirs("financer", version="0.1.0")))
    #appdata.ensure_app_data_exists()

    repo = DocumentRepo()

    try:
        budget = repo.get_budgets()[0]
    except IndexError:
        budget = Budget("My Budget")
        repo.save_budget(budget)


    def slot():
        repo.save_budget(budget)

    app = QApplication([])
    window = QMainWindow()
    window.setWindowTitle(f"Budget: {budget.name}")

    shortcut = QShortcut(QKeySequence("Ctrl+S"), window)
    shortcut.activated.connect(slot)

    # setup stylesheet
    #apply_stylesheet(app, theme='light_amber.xml')

    window.setCentralWidget(build_layout(budget))
    window.resize(1200, 800)
    window.show()

    sys.exit(app.exec())
