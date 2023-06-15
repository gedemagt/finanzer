from dash_extensions.enrich import Trigger, Output, html, Input, DashBlueprint
from finance.model.entry import Budget
import dash_mantine_components as dmc

from finance.webapp.state import repo


bp = DashBlueprint()


def create_summary(budget: Budget):
    return dmc.Grid([
        dmc.Col([
            dmc.Card([
                dmc.Group(
                    children=[
                        dmc.Text("Indkomst"),
                    ],
                    position="center",
                ),
                dmc.Center([
                    dmc.Text(f"DKK ", size="xs", mr="xs"),
                    dmc.Text(f"{sum(x.total_monthly() for x in budget.incomes):0.0f}", size="lg", weight=700)
                ])
            ], withBorder=True)
        ], span=4),
        dmc.Col([
            dmc.Card([
                dmc.Group(
                    children=[
                        dmc.Text("Udgifter"),
                    ],
                    position="center",
                ),
                dmc.Center([
                    dmc.Text(f"DKK ", size="xs", mr="xs"),
                    dmc.Text(f"{sum(x.total_monthly() for x in budget.expenses):0.0f}", size="lg", weight=700)
                ])
            ], withBorder=True)
        ], span=4),
        dmc.Col([
            dmc.Card([
                dmc.Group(
                    children=[
                        dmc.Text("Balance"),
                    ],
                    position="center",
                ),
                dmc.Center([
                    dmc.Text(f"DKK ", size="xs", mr="xs"),
                    dmc.Text(f"{sum(x.total_monthly() for x in budget.incomes) - sum(x.total_monthly() for x in budget.expenses):0.0f}", size="lg", weight=700)
                ])
            ], withBorder=True)
        ], span=4)
    ])


@bp.callback(
    Input('selected-budget', 'data'),
    Trigger("change-store", "data"),
    Output("balance-summary", "children")
)
def _on_change(budget_idx: int):
    return [create_summary(repo.get_budget(budget_idx))]


bp.layout = html.Div([
    html.Div(id="balance-summary")
])
