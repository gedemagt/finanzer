import os

from PySide6.QtCore import QSize
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QToolBar, QFileDialog


class Toolbar(QToolBar):

    def __init__(self):
        super().__init__("John")

        self.setIconSize(QSize(16, 16))

        self.new_button = QAction("New", self)

        self.addAction(self.new_button)

        self.addSeparator()

        self.load_button = QAction("Load", self)
        self.addAction(self.load_button)

    def set_on_new(self, callback):
        self.new_button.triggered.connect(callback)

    def set_on_load(self, callback):

        def _callback():
            file_name, _filter = QFileDialog.getOpenFileName(self, "Open budget-file", os.getcwd(), "*.json")
            callback(file_name)

        self.load_button.triggered.connect(_callback)
