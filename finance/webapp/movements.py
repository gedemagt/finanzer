from datetime import datetime

from dash_extensions.enrich import DashProxy, Trigger, Output, html, Input

from finance.model.entry import Budget
import dash_mantine_components as dmc
from finance.utils.monthly_overview import get_monthly_movements, MONTHS
from finance.webapp.state import repo


def create_movements(budget: Budget):

    groups = get_monthly_movements(budget, "Budget", range(1, 12))

    children = []

    block = datetime.now().month // 3 - 1
    gs = [block*3+1, block*3+2, block*3+3]
    size = max(len(groups[x]) for x in gs)
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
        for x in sorted(groups[g], key=lambda _x: (_x.payment_period, _x.name)):
            rows.append(html.Tr([html.Td(x.name, style={"font-size": "12px"}), html.Td(x.payment_size, style={"text-align": "right", "font-size": "12px"}), html.Td(dmc.Checkbox())]))
        rows += [html.Tr([html.Td("-"), html.Td("-", style={"text-align": "right"})]) for _ in range(size - len(groups[g]))]

        rows.append(html.Tr([
            html.Td(dmc.Text("Total", weight=700)),
            html.Td(dmc.Text(sum(x.payment_size for x in groups[g]), weight=700), style={"text-align": "right"})
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
        Trigger("change-store", "data"),
        Output("movements", "children")
    )
    def _on_change(budget_idx: str):
        return [create_movements(repo.get_budget(budget_idx))]

    return html.Div([
        html.Div(id="movements")
    ])

