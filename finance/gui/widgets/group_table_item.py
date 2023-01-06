from PySide6.QtGui import QColor
from PySide6.QtWidgets import QTableWidgetItem


class GroupTableWidget(QTableWidgetItem):

    def __init__(self, name: str, color: QColor):
        QTableWidgetItem.__init__(self, name)
        self.old_name = name
        self.setBackground(color)
