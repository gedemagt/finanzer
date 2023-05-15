from enum import Enum
from typing import List, Type

from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import QComboBox

from finance.gui.widgets.group_table_item import GroupTableWidget

MONTHS = [
    "Januar", "Februar", "Marts", "April", "Maj", "Juni",
    "Juli", "August", "September", "Oktober", "November", "December"
]
PAYMENT_METHODS = ["BS", "Kort", "MobilePay", "Overførsel"]
PERIODS = {
    "Månedvis": 1,
    "Kvartalsvis": 3,
    "Halvårlig": 6,
    "Årlig": 12
}


def create_header_font():
    font = QFont()
    font.setBold(True)
    return font


def group_header_item(name: str, color: QColor):
    group_header = GroupTableWidget(name, color)
    group_header.setFont(create_header_font())
    return group_header


def create_month_combobox(entry, prop):
    cb = QComboBox()
    cb.addItems(MONTHS)
    cb.setCurrentIndex(getattr(entry, prop)-1)

    def on_change():
        setattr(entry, prop, cb.currentIndex()+1)

    cb.currentTextChanged.connect(on_change)
    return cb


def create_period_combobox(entry, prop):
    cb = QComboBox()
    cb.addItems(PERIODS.keys())
    cb.setCurrentIndex(list(PERIODS.values()).index(getattr(entry, prop)))

    def on_change():
        setattr(entry, prop, PERIODS[cb.currentText()])

    cb.currentTextChanged.connect(on_change)
    return cb


def create_enum_combobox(entry, prop, enum: Type[Enum]):
    cb = QComboBox()
    cb.addItems([x.value for x in enum])
    cb.setCurrentText(getattr(entry, prop))

    def on_change():
        setattr(entry, prop, enum(cb.currentText()))

    cb.currentTextChanged.connect(on_change)
    return cb


def create_payment_combobox(entry, prop):
    cb = QComboBox()
    cb.addItems(PAYMENT_METHODS)
    cb.setCurrentText(getattr(entry, prop))

    def on_change():
        setattr(entry, prop, cb.currentText())

    cb.currentTextChanged.connect(on_change)
    return cb


def create_account_combobox(entry, prop, accounts: List[str]):
    cb = QComboBox()
    cb.addItems(accounts)
    cb.setCurrentText(getattr(entry, prop))

    def on_change():
        setattr(entry, prop, cb.currentText())

    cb.currentTextChanged.connect(on_change)
    return cb
