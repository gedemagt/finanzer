from datetime import datetime

from dash.exceptions import PreventUpdate
from dash_extensions.enrich import DashProxy, Trigger, Output, html, Input

from finance.model.entry import Budget
import dash_mantine_components as dmc
from finance.utils.monthly_overview import get_monthly_movements, MONTHS
from finance.webapp.state import repo, BudgetNotFoundError


def create_movements(budget: Budget, block: int = None):

    groups = get_monthly_movements(budget, "Budget", range(1, 12))

    if block is None:
        block = datetime.now().month // 3 - 1
    gs = [block*3+1, block*3+2, block*3+3]
    size = max(len(groups[x]) for x in gs)

    children = [
        dmc.Col([
            dmc.Select(
                id="block-select",
                data=[
                    {"label": f"{MONTHS[0]}-{MONTHS[2]}", "value": 0},
                    {"label": f"{MONTHS[3]}-{MONTHS[5]}", "value": 1},
                    {"label": f"{MONTHS[6]}-{MONTHS[8]}", "value": 2},
                    {"label": f"{MONTHS[9]}-{MONTHS[11]}", "value": 3},
                ],
                value=block
            )
        ], span=12, mt=3, className="text-center")
    ]

    for g in gs:
        header = [
            html.Thead(
                html.Tr(
                    [
                        html.Th("Udgift"),
                        html.Th("Beløb"),
                        html.Th("")
                    ]
                )
            )
        ]

        rows = []
        for x in sorted(groups[g-1], key=lambda _x: (_x.payment_period, _x.name)):
            rows.append(html.Tr([html.Td(x.name, style={"font-size": "12px"}), html.Td(x.payment_size, style={"text-align": "right", "font-size": "12px"}), html.Td(dmc.Checkbox())]))
        rows += [html.Tr([html.Td("-"), html.Td("-", style={"text-align": "right"})]) for _ in range(size - len(groups[g-1]))]

        rows.append(html.Tr([
            html.Td(dmc.Text("Total", weight=700)),
            html.Td(dmc.Text(sum(x.payment_size for x in groups[g-1]), weight=700), style={"text-align": "right"})
        ]))

        body = [html.Tbody(rows)]
        children.append(
            dmc.Col([
                dmc.Card([
                    dmc.Center(dmc.Text(MONTHS[g-1])),
                    dmc.CardSection([
                        dmc.Table(header + body)
                    ])
                ], withBorder=True, mt="sm")
            ], span=4),
        )

    return dmc.Grid(children)


def init(app: DashProxy):

    @app.callback(
        Input("selected-budget", "data"),
        Input("selected-block", "data"),
        Trigger("change-store", "data"),
        Output("movements", "children")
    )
    def _on_change(budget_idx: str, block: int):
        try:
            return [create_movements(repo.get_budget(budget_idx), block)]
        except BudgetNotFoundError:
            raise PreventUpdate()

    @app.callback(
        Input("block-select", "value"),
        Output("selected-block", "data"),
        prevent_initial_call=True
    )
    def _on_change(block: int):
        return block

    return html.Div([
        html.Div(id="movements")
    ])

