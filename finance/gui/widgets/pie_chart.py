from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCharts import QChart, QChartView, QPieSeries

from finance.model.entry import Budget


class TestChart(QWidget):

    def __init__(self, budget: Budget):
        super().__init__()

        self.series = QPieSeries()

        budget_monthly = budget.total_monthly()
        for group in budget.expenses:
            monthly = group.total_monthly()
            try:
                self.series.append(f"<b>{group.name}</b><br> {int(monthly)} ({group.total_monthly()/budget_monthly*100:0.1f}%)", monthly)
            except ZeroDivisionError:
                self.series.append(
                    f"<b>{group.name}</b><br> {int(monthly)} (-%)", monthly)

        self.chart = QChart()
        self.chart.addSeries(self.series)

        self.chart.legend().hide()
        for s in self.series.slices():
            s.setLabelVisible()

        self._chart_view = QChartView(self.chart)
        self._chart_view.setRenderHint(QPainter.Antialiasing)

        layout = QVBoxLayout()
        layout.addWidget(self._chart_view)
        self.setLayout(layout)
