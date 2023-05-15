from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QLayout

from finance.model.entry import Budget


class MonthlyOverview(QWidget):

    def __init__(self, budget: Budget):
        super().__init__()
        self.budget = budget

        self._layout = QHBoxLayout()

        self._layout.addWidget(QLabel(f"Total indkomst: {budget.total_monthly_income()}"))
        self._layout.addWidget(QLabel(f"Total udgift: {budget.total_monthly()}"))
        self._layout.addWidget(QLabel(f"Balance: {budget.total_monthly_income() - budget.total_monthly()}"))

        self._layout.setSizeConstraint(QLayout.SizeConstraint.SetMaximumSize)
        self.setLayout(self._layout)
