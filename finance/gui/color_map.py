from PySide6.QtGui import QColor

INCOME_COLOR = QColor.fromRgb(75, 191, 75, 255)
EXPENSE_COLOR = QColor.fromRgb(191, 82, 75, 255)


def color_map_distinct():
    "https://colorbrewer2.org/#type=qualitative&scheme=Paired&n=12"
    return iter([
        QColor(166, 206, 227),
        QColor(31, 120, 180),
        QColor(178, 223, 138),
        QColor(51, 160, 44),
        QColor(251, 154, 153),
        QColor(227, 26, 28),
        QColor(253, 191, 111),
        QColor(255, 127, 0),
        QColor(202, 178, 214),
        QColor(106, 61, 154),
        QColor(255, 255, 153),
        QColor(177, 89, 40)
    ])
