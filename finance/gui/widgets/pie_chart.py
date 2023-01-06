from PySide6.QtGui import QPainter, Qt
from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtCharts import QChart, QChartView, QBarSet, QValueAxis, QStackedBarSeries, QBarCategoryAxis

from finance.model.entry import Budget
from finance.utils import clearLayout


class TestChart(QWidget):

    def __init__(self, budget: Budget):
        super().__init__()

        self._budget = budget
        self._expense_widget = self._build(budget)

        self.layout = QHBoxLayout()
        self.layout.addWidget(self._expense_widget)
        self.setLayout(self.layout)

        budget.register_on_update(self._update)

    def _build(self, budget: Budget) -> QWidget:
        series = QStackedBarSeries()

        budget_monthly = budget.total_monthly()

        expenses = []

        for group in budget.expenses:
            monthly = group.total_monthly()
            expenses.append((f"({monthly / budget_monthly * 100:00.0f}%) {group.name}", monthly))

        for name, expense in sorted(expenses, key=lambda x: x[1]):
            month_set = QBarSet(name)
            month_set.append(expense / 1000)
            month_set.append(0)
            series.append(month_set)

        for group in budget.incomes:
            month_set = QBarSet(group.name)
            month_set.append(0)
            month_set.append(group.total_monthly()/1000)
            series.append(month_set)

        chart = QChart()
        chart.addSeries(series)

        chart.legend().setAlignment(Qt.AlignLeft)
        _chart_view = QChartView(chart)
        _chart_view.setRenderHint(QPainter.Antialiasing)

        axisY = QValueAxis()
        axisY.setRange(0, max(budget.total_monthly_income(), budget.total_monthly())*1.1 // 1000)
        chart.addAxis(axisY, Qt.AlignLeft)
        series.attachAxis(axisY)

        axisX = QBarCategoryAxis()
        axisX.append(["Expenses", "Incomes"])
        chart.addAxis(axisX, Qt.AlignBottom)

        return _chart_view

    def _update(self, *args):

        clearLayout(self.layout)

        self.layout.addWidget(self._build(self._budget))
