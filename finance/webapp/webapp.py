from appdata import appdata
from dash_extensions.enrich import DashProxy, html, dcc, TriggerTransform, \
    NoOutputTransform, Trigger, Output, Input, State

import dash_mantine_components as dmc
from dash_iconify import DashIconify

from finance.model.entry import Budget
from finance.webapp import expense_income_graph, income_table, transfer_table, accounts_table, balance_summary, \
    movements
from finance.webapp import expense_table
from finance.webapp import saldo_graph

app = DashProxy(
    transforms=[
        TriggerTransform(), NoOutputTransform()
    ],
    external_stylesheets=[
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css'
    ]
)

try:
    budget = Budget.load(appdata["last_budget"])
except (KeyError, FileNotFoundError):
    budget = Budget("My Budget")


@app.callback(
    Trigger("save-btn", "n_clicks"),
    Output("save-btn", "disabled", allow_duplicate=True),
    prevent_initial_call=True
)
def save_budget():
    budget.save()
    return True


@app.callback(
    Trigger("change-store", "data"),
    Output("save-btn", "disabled", allow_duplicate=True),
    prevent_initial_call=True
)
def show_save():
    return False


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='change-store', data="Erik123", storage_type='local'),
    dmc.Header(
        height=50, children=[
            dmc.ActionIcon(
                DashIconify(icon="material-symbols:save", height=24),
                variant='filled',
                color="blue",
                size="lg",
                id="save-btn",
                disabled=True,
                m="10px"
            )
        ]
    ),
    html.Div(id='page-content', children=[
        dmc.Grid([
            dmc.Col([
                dmc.Tabs(
                    [
                        dmc.TabsList(
                            [
                                dmc.Tab("Udgifter", value="expenses"),
                                dmc.Tab("Indkomst", value="incomes"),
                                dmc.Tab("Overførsler", value="transfers"),
                                dmc.Tab("Konti", value="accounts")
                            ]
                        ),
                        dmc.TabsPanel(expense_table.init(app, budget), value="expenses"),
                        dmc.TabsPanel(income_table.init(app, budget), value="incomes"),
                        dmc.TabsPanel(transfer_table.init(app, budget), value="transfers"),
                        dmc.TabsPanel(accounts_table.init(app, budget), value="accounts")
                    ],
                    value="expenses",
                    m="sm"
                )
            ], span=7),
            dmc.Col([
                html.Div(id="upper-right", children=[
                    dmc.Tabs(
                        [
                            dmc.TabsList(
                                [
                                    dmc.Tab("Fordeling", value="overview"),
                                    dmc.Tab("Saldo", value="saldo"),
                                    dmc.Tab("Månedsudgifter", value="movements")
                                ]
                            ),
                            dmc.TabsPanel(expense_income_graph.init(app, budget), value="overview"),
                            dmc.TabsPanel(saldo_graph.init(app, budget), value="saldo"),
                            dmc.TabsPanel(movements.init(app, budget), value="movements")
                        ],
                        value="saldo",
                        m="sm"
                    ),
                ]),
                dmc.Container([
                    balance_summary.init(app, budget)
                ], m="sm")
            ], span=5)
        ])
    ], style=dict(height="calc(100vh - 50px)"))
])

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    app.run_server(
        debug=True
    )
