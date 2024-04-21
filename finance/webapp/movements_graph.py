from collections import defaultdict
from typing import Optional

from dash import html
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import DashProxy, Trigger, Output, Input, State
from finance.model.entry import Budget
import dash_cytoscape as cyto

from finance.webapp.models import ChangeStoreModel
from finance.webapp.state import repo, BudgetNotFoundError


class Edge:

    def __init__(self, transfer = 0.0, start: Optional = None, end: Optional = None):
        self.start: Optional[Node] = start
        self.end: Optional[Node] = end
        self.transfer: float = transfer


class Node:

    def __init__(self, account: str, level: int = 0, tag: str = "acc"):
        self.account: str = account
        self.incoming: list[Edge] = []
        self.outgoing: list[Edge] = []
        self.balance: float = 0.0
        self.level: int = level
        self.tag: str = tag


def create_figure(budget: Budget):

    graph: dict[str, Node] = {}
    edges = []

    for x in budget.incomes:
        for i in x.entries:

            inc_node = Node(i.name, level=-1, tag="inc")

            if i.account not in graph:
                graph[i.account] = Node(i.account)

            e = Edge(i.monthly(), start=i.name, end=i.account)
            graph[i.account].incoming.append(e)
            inc_node.outgoing.append(e)
            graph[i.name] = inc_node
            edges.append(e)

    for x in budget.transfers:

        n_last = graph[x.source]

        if x.destination not in graph:
            graph[x.destination] = Node(x.destination, n_last.level + 1)

        edge = Edge(x.amount, start=x.source, end=x.destination)

        graph[x.source].outgoing.append(edge)
        graph[x.destination].incoming.append(edge)
        edges.append(edge)

    nodes = defaultdict(list)
    for n in graph.values():
        nodes[n.level].append(n)

    elements = [
        {'data': {'source': e.start, 'target': e.end, 'label': str(int(e.transfer))},
         'style': {
             'edge-text-rotation': 'autorotate',
             'text-background-color': '#ffffff',
             'text-background-opacity': 1
         }}
        for e in edges
    ]

    dh = 100

    height = 5 * dh

    expense_balances, income_balances, transfer_balances = budget.calculate_balances()

    balance = {}
    for account in budget.accounts:
        balance[account.name] = income_balances[account.name] + transfer_balances[
            account.name] + expense_balances[account.name]

    for level in sorted(nodes):
        n_nodes = len(nodes[level])
        for idx, n in enumerate(nodes[level]):
            if n.account in balance:
                b = str(int(balance[n.account]))
            else:
                b = ''
            elements.append(
                {'data': {'id': n.account, 'label': f"{n.account}\n{b}",
                          'tag': n.tag},
                 'position': budget.extra.get("account-layout", {}).get(n.account, {'y': height / (n_nodes + 1) * (idx + 1), 'x': level * 500}),
                 'style': {
                     'background-color': 'red' if balance.get(n.account, 0.0) < 0 else 'blue',
                     'text-wrap': 'wrap',
                     'color': 'white',
                     'text-outline-color': 'white',
                     'font-weight': 'bold'
                 }
                }
            )

    fig = cyto.Cytoscape(
        id='cytoscape-two-nodes',
        layout={'name': 'preset'},
        style={'width': '100%', 'height': '600px'},
        elements=elements,
        stylesheet=[
            {
                'selector': 'node',
                'style': {
                    'label': 'data(label)'
                }
            },
            {
                'selector': 'edge',
                'style': {
                    'label': 'data(label)'
                }
            },
            {
                'selector': '[tag = "inc"]',
                'style': {
                    'shape': 'rectangle',
                    'background-color': 'green'
                }
            },
            {
                'selector': 'edge',
                'style': {
                    # The default curve style does not work with certain arrows
                    'curve-style': 'bezier'
                }
            },
            {
                'selector': 'edge',
                'style': {
                    'target-arrow-shape': 'triangle',
                }
            },
            {
                'selector': 'node',
                'style': {
                    'content': 'data(label)',
                    'text-halign': 'center',
                    'text-valign': 'center',
                    'width': '150px',
                    'height': '60px',
                    'shape': 'square'
                }
            }
        ]
    )

    return fig


def init(app: DashProxy):

    @app.callback(
        Output('change-store', 'data', allow_duplicate=True),
        Input('cytoscape-two-nodes', 'elements'),
        State('selected-budget', 'data'),
    )
    def _on_edit(e, budget_idx):

        state = {}

        for x in e:
            if 'position' in x:
                state[x['data']['id']] = x.get("position")

        try:
            budget = repo.get_budget(budget_idx)

            if state == budget.extra.get("account-layout"):
                raise PreventUpdate()

            budget.add_extra("account-layout", state)
            return ChangeStoreModel(budget_idx)
        except BudgetNotFoundError:
            raise PreventUpdate()

    @app.callback(
        Input('selected-budget', 'data'),
        Trigger("change-store", "data"),
        Output("movements-graph", "children")
    )
    def _on_change(budget_idx: str):
        try:
            return create_figure(repo.get_budget(budget_idx))
        except BudgetNotFoundError:
            raise PreventUpdate()

    return html.Div(id="movements-graph")
