from dash.exceptions import PreventUpdate
from dash_extensions.enrich import DashProxy, Trigger, dcc, Output, Input
from finance.model.entry import Budget


import plotly.graph_objects as go

from finance.utils.monthly_overview import monthly, expected_saldo
from finance.webapp.state import repo, BudgetNotFoundError


def create_figure(budget: Budget):

    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dec']

    monthly_expenses, monthly_incomes = monthly(budget, "Budget")

    saldos = expected_saldo(monthly_expenses)

    fig = go.Figure()
    fig.add_trace(go.Bar(x=months, y=monthly_incomes, name='Income'))
    fig.add_trace(go.Bar(x=months, y=monthly_expenses, name='Expenses'))
    fig.add_trace(go.Bar(x=months, y=saldos, name='Saldo'))

    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
    )
    return fig


def init(app: DashProxy):

    @app.callback(
        Input('selected-budget', 'data'),
        Trigger("change-store", "data"),
        Output("saldo-graph", "figure")
    )
    def _on_change(budget_idx: str):
        try:
            return create_figure(repo.get_budget(budget_idx))
        except BudgetNotFoundError:
            raise PreventUpdate()

    return dcc.Graph(id="saldo-graph")
