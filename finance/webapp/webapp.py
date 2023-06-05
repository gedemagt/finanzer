from uuid import uuid4

from appdata import appdata
from dash import ALL, Input
from dash_extensions.enrich import DashProxy, html, dcc, TriggerTransform, \
    NoOutputTransform, Trigger, Output

import dash_mantine_components as dmc
from dash_extensions.snippets import get_triggered
from dash_iconify import DashIconify

from finance.model.entry import Budget
from finance.webapp import expense_income_graph, income_table, transfer_table, accounts_table, balance_summary, \
    movements
from finance.webapp import expense_table
from finance.webapp import saldo_graph
from finance.webapp.state import get_budget, budgets, set_budget

app = DashProxy(
    transforms=[
        TriggerTransform(), NoOutputTransform()
    ],
    external_stylesheets=[
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css'
    ], suppress_callback_exceptions=True
)

@app.callback(
    Trigger("save-btn", "n_clicks"),
    Output("save-btn", "disabled", allow_duplicate=True),
    prevent_initial_call=True
)
def save_budget():
    get_budget().save()
    return True


@app.callback(
    Trigger("change-store", "data"),
    Output("save-btn", "disabled", allow_duplicate=True),
    prevent_initial_call=True
)
def show_save():
    return False


@app.callback(
    Trigger(dict(type="select-budget", budget=ALL), "n_clicks"),
    Output("change-store", "data"),
    prevent_initial_call=True
)
def select_budget():
    t = get_triggered()
    budget_idx = t.id["budget"]
    set_budget(budget_idx)
    return str(uuid4())


@app.callback(
    Input("add-budget-btn", "n_clicks"),
    Output("budget-list", "children"),
    Output("selected-budget", "data", allow_duplicate=True)
)
def select_budget(n_clicks):
    if n_clicks is not None:
        budgets.append(Budget("New budget"))
    return [
        dmc.NavLink(
            id=dict(type="select-budget", budget=idx),
            label=budget.name,
            icon=DashIconify(icon="bi:house-door-fill", height=16),
            active=True
        ) for idx, budget in enumerate(budgets)
    ], len(budgets)-1


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='change-store', data="Erik123", storage_type='local'),
    dcc.Store(id='selected-budget', data=0, storage_type='local'),
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
                html.Div(
                    children=[
                        html.Div(id="budget-list"),
                        dmc.NavLink(
                            id="add-budget-btn",
                            label="Add budget",
                            icon=DashIconify(icon="bi:plus-fill", height=16),
                        )
                    ]
                )
            ], span=1),
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
                        dmc.TabsPanel(expense_table.init(app), value="expenses"),
                        dmc.TabsPanel(income_table.init(app), value="incomes"),
                        dmc.TabsPanel(transfer_table.init(app), value="transfers"),
                        dmc.TabsPanel(accounts_table.init(app), value="accounts")
                    ],
                    value="expenses",
                    m="sm"
                )
            ], span=6),
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
                            dmc.TabsPanel(expense_income_graph.init(app), value="overview"),
                            dmc.TabsPanel(saldo_graph.init(app), value="saldo"),
                            dmc.TabsPanel(movements.init(app), value="movements")
                        ],
                        value="saldo",
                        m="sm"
                    ),
                ]),
                dmc.Container([
                    balance_summary.init(app)
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
