from dash_extensions.enrich import DashProxy, Trigger, dcc, Output
from finance.model.entry import Budget


import plotly.graph_objects as go

from finance.utils.monthly_overview import monthly, expected_saldo


def create_figure(budget: Budget):

    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dec']

    monthly_expenses, monthly_incomes = monthly(budget, "Budget")

    # average_expense = sum(monthly_expenses) / 12
    # average_income = sum(monthly_incomes) / 12
    #
    # diff = sum(monthly_incomes) - sum(monthly_expenses)

    saldos = expected_saldo(monthly_expenses, monthly_incomes)

    fig = go.Figure()
    fig.add_trace(go.Bar(x=months, y=monthly_incomes, name='Income'))
    fig.add_trace(go.Bar(x=months, y=monthly_expenses, name='Expenses'))
    fig.add_trace(go.Bar(x=months, y=saldos, name='Saldo'))

    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
    )
    return fig


def init(app: DashProxy, budget: Budget):

    @app.callback(
        Trigger("change-store", "data"),
        Output("saldo-graph", "figure")
    )
    def _on_change():
        return create_figure(budget)

    return dcc.Graph(id="saldo-graph", figure=create_figure(budget))