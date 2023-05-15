from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidgetItem


class ProppedTableWidget(QTableWidgetItem):

    def __init__(self, entry, prop: str, editable=True):
        self.entry = entry
        self.prop = prop
        self.type = entry.__annotations__[prop]

        alignment = Qt.AlignVCenter

        val = getattr(self.entry, prop)
        if isinstance(val, float):
            val = f"{val:0.2f}"
            alignment |= Qt.AlignRight
        else:
            val = str(val)

        super().__init__(val)

        self.setTextAlignment(alignment)
        if not editable:
            self.setFlags(~Qt.ItemIsEditable)

        setattr(self, "setData", self._set_data)

    def value(self):
        return getattr(self.entry, self.prop)

    def _set_data(self, role: int, value: Any) -> None:
        if role == 2:
            try:
                converted = self.type(value)
                super().setData(role, converted)
                setattr(self.entry, self.prop, converted)
            except ValueError:
                pass
        else:
            super().setData(role, value)
