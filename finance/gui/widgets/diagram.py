from typing import List

from PySide6.QtCore import QRect
from PySide6.QtGui import QPainter, Qt
from PySide6.QtWidgets import QWidget

from finance.gui.color_map import EXPENSE_COLOR, INCOME_COLOR
from finance.model.entry import Budget, EntryGroup, Account


WIDTH = 150
HEIGHT = 30
PADDING = 5
entry_height = HEIGHT - 2*PADDING
entry_width = WIDTH - 2*PADDING


class Node:

    def __init__(self, text: str, value: float, x: int = 0, y: int = 0):
        self.text = text
        self.value = value
        self.x = x
        self.y = y
        self.connections: List[Node] = []

    def connect_to(self, node):
        self.connections.append(node)

    def draw(self, qp: QPainter):
        qp.drawRect(QRect(self.x + PADDING, self.y + PADDING, entry_width, entry_height))
        qp.drawText(QRect(self.x + PADDING * 2, self.y + PADDING, entry_width - PADDING, HEIGHT), Qt.AlignLeft, self.text)
        qp.drawText(QRect(self.x + PADDING * 2, self.y + PADDING, entry_width - PADDING, HEIGHT), Qt.AlignRight,
                    f"{self.value:0.1f}")

        for x in self.connections:
            qp.drawLine(self.x + WIDTH, self.y + HEIGHT // 2, x.x, x.y + HEIGHT // 2)


class Diagram(QWidget):

    def __init__(self, budget: Budget):
        super().__init__()

        self._budget = budget

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)

        income = self._budget.incomes[0].entries[0]
        income_node = Node(income.name, income.monthly(), 10, 10)

        expense = self._budget.expenses[0].entries[0]
        expense_node = Node(expense.name, expense.monthly(), 400, 10)

        account = self._budget.accounts[0]
        account_node = Node(account.name, 0, 200, 10)

        income_node.connect_to(account_node)
        account_node.connect_to(expense_node)

        income_node.draw(qp)
        account_node.draw(qp)
        expense_node.draw(qp)

        qp.end()

    def draw_expense_group(self, qp, x, y, grp: EntryGroup):

        qp.setBrush(EXPENSE_COLOR)

        for e in grp.entries:
            node = Node(e.name, e.monthly(), x, y)
            node.draw(qp)
            y += HEIGHT

        return y

    def draw_accounts(self, qp, x, y, accounts: List[Account]):

        qp.setBrush(INCOME_COLOR)
        for a in accounts:
            node = Node(a.name, 0, x, y)
            node.draw(qp)

            y += HEIGHT

        return y

    def draw_income_group(self, qp, x, y, grp: EntryGroup):

        qp.setBrush(INCOME_COLOR)
        for e in grp.entries:
            node = Node(e.name, e.monthly(), x, y)
            node.draw(qp)

            y += HEIGHT

        return y

    def draw_expenses(self, qp):

        y = 10
        x = 10
        for grp in self._budget.incomes:
            y += self.draw_income_group(qp, x, y, grp)

        x = 2 * WIDTH
        y = 10

        y += self.draw_accounts(qp, x, y, [x for x in self._budget.accounts if not x.spending])

        x = 3 * WIDTH
        y = 10
        y += self.draw_accounts(qp, x, y, [x for x in self._budget.accounts if x.spending])

        x = 5 * WIDTH
        y = 10

        for grp in self._budget.expenses:
            y += self.draw_expense_group(qp, x, y, grp)

