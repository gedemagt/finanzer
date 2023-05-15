from PySide6.QtGui import QPainter, Qt
from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtCharts import QChart, QChartView, QBarSet, QValueAxis, QStackedBarSeries, QBarCategoryAxis

from finance.gui.color_map import color_map_distinct
from finance.model.entry import Budget


def clear_layout(layout):
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()


class BarChart(QWidget):

    def __init__(self, budget: Budget):
        super().__init__()

        self._budget = budget
        self._expense_widget = self._build()

        self.layout = QHBoxLayout()
        self.layout.addWidget(self._expense_widget)
        self.setLayout(self.layout)

        budget.register_on_update(self._update)

    def _build(self) -> QWidget:
        series = QStackedBarSeries()

        budget_monthly = self._budget.total_monthly()

        expenses = []

        color_iter_expenses = color_map_distinct()
        color_iter_incomes = color_map_distinct()

        for group in self._budget.expenses:
            monthly = group.total_monthly()
            expenses.append((f"({monthly / budget_monthly * 100:00.0f}%) {group.name}", monthly))

        for name, expense in sorted(expenses, key=lambda x: x[1], reverse=True):
            month_set = QBarSet(name)
            month_set.setColor(next(color_iter_expenses))
            month_set.append(expense / 1000)
            month_set.append(0)
            series.append(month_set)

        for group in self._budget.incomes:
            month_set = QBarSet(group.name)
            month_set.setColor(next(color_iter_incomes))
            month_set.append(0)
            month_set.append(group.total_monthly() / 1000)
            series.append(month_set)

        chart = QChart()
        chart.addSeries(series)

        chart.legend().setAlignment(Qt.AlignLeft)
        _chart_view = QChartView(chart)
        _chart_view.setRenderHint(QPainter.Antialiasing)

        axisY = QValueAxis()
        axisY.setRange(0, max(self._budget.total_monthly_income(), self._budget.total_monthly())*1.1 // 1000)
        chart.addAxis(axisY, Qt.AlignLeft)
        series.attachAxis(axisY)

        axisX = QBarCategoryAxis()
        axisX.append(["Expenses", "Incomes"])
        chart.addAxis(axisX, Qt.AlignBottom)

        return _chart_view

    def _update(self, *args):
        clear_layout(self.layout)
        self.layout.addWidget(self._build())
