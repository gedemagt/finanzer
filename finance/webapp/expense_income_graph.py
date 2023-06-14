from dash_extensions.enrich import DashProxy, Trigger, dcc, Output, html, Input, DashBlueprint
from finance.model.entry import Budget


import plotly.graph_objects as go

from finance.webapp.state import repo

bp = DashBlueprint()


def create_figure(budget: Budget):
    fig = go.Figure()
    total_monthly = sum(x.total_monthly() for x in budget.expenses)
    for eg in sorted(budget.expenses, key=lambda x: x.total_monthly()):
        fig.add_trace(go.Bar(
            x=["Udgifter"], y=[eg.total_monthly()],
            name=f"({eg.total_monthly() / total_monthly * 100:3.0f}%) {eg.name}",
            legendgroup="group0",
            legendgrouptitle_text="Udgifter",
        ))

    if len(budget.incomes) == 1:
        for eg in sorted(budget.incomes[0].entries, key=lambda x: x.monthly()):
            fig.add_trace(go.Bar(
                x=["Indkomst"], y=[eg.monthly()],
                name=eg.name,
                legendgroup="group1",
                legendgrouptitle_text="Indkomst",
            ))
    else:
        for eg in sorted(budget.incomes, key=lambda x: x.total_monthly()):
            fig.add_trace(go.Bar(
                x=["Indkomst"], y=[eg.total_monthly()],
                name=eg.name,
                legendgroup="group1",
                legendgrouptitle_text="Indkomst",
            ))

    fig.update_layout(barmode='stack')
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
    )
    return fig


@bp.callback(
    Input('selected-budget', 'data'),
    Trigger("change-store", "data"),
    Output("income-graph", "figure")
)
def _on_change(budget_idx: int):
    return create_figure(repo.get_budget(budget_idx))


bp.layout = html.Div([
    dcc.Graph(id="income-graph")
])
