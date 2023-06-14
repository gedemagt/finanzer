from uuid import uuid4

from appdata import appdata
from dash import ALL, Input
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import DashProxy, html, dcc, TriggerTransform, \
    NoOutputTransform, Trigger, Output, State, PrefixIdTransform

import dash_mantine_components as dmc
from dash_extensions.snippets import get_triggered
from dash_iconify import DashIconify

from finance.webapp import expense_income_graph, income_table, transfer_table, accounts_table, balance_summary, \
    movements
from finance.webapp import expense_table
from finance.webapp import saldo_graph
from finance.webapp.accounts_table import bp
from finance.webapp.balance_summary import balance_summary_bp
from finance.webapp.models import ChangeStoreModel
from finance.webapp.state import repo
from finance.webapp.transform import DataclassTransform

app = DashProxy(
    transforms=[
        TriggerTransform(), NoOutputTransform(), DataclassTransform()
    ],
    external_stylesheets=[
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css'
    ], suppress_callback_exceptions=True
)

repo.set_directory(appdata.get("budget_directory", "budgets"))


@app.callback(
    Trigger("save-btn", "n_clicks"),
    Output("dirty", "data", allow_duplicate=True),
    State('selected-budget', 'data'),
    State("dirty", "data"),
    prevent_initial_call=True
)
def save_budget(budget_idx: int, dirty: list):
    repo.get_budget(budget_idx).save()
    if budget_idx in dirty:
        dirty.remove(budget_idx)
    print("Erik", dirty, budget_idx)
    return dirty


@app.callback(
    Input("selected-budget", "data"),
    Input("dirty", "data"),
    Output("save-btn", "disabled"),
    prevent_initial_call=True
)
def show_save(budget_idx: int, dirty: list):
    print(budget_idx, dirty)
    return budget_idx not in dirty


@app.callback(
    Input("change-store", "data"),
    Output("dirty", "data", allow_duplicate=True),
    State("dirty", "data"),
    prevent_initial_call=True
)
def mark_dirty(change_store: ChangeStoreModel, dirty: list):
    idx = change_store.budget_idx
    if idx is not None:
        if idx not in dirty:
            dirty.append(idx)
    return dirty


@app.callback(
    Trigger("selected-budget", "data"),
    Output("change-store", "data"),
    State("change-store", "data"),
    prevent_initial_call=True
)
def changed(current_state):
    current_state["correlation"] = str(uuid4())
    return current_state


@app.callback(
    Trigger(dict(type="select-budget", budget=ALL), "n_clicks"),
    Output("selected-budget", "data", allow_duplicate=True),
    prevent_initial_call=True
)
def select_budget():
    t = get_triggered()
    if t.n_clicks is not None:
        budget_idx = t.id["budget"]
        return budget_idx
    else:
        raise PreventUpdate()


@app.callback(
    Input("selected-budget", "data"),
    Output("budget-list", "children")
)
def select_budget(selected_idx: int):
    return [
        dmc.NavLink(
            id=dict(type="select-budget", budget=idx),
            label=budget.name,
            icon=DashIconify(icon="bi:house-door-fill", height=16),
            active=idx == selected_idx
        ) for idx, budget in enumerate(repo.budgets)
    ]


@app.callback(
    Output("copy-select", "value"),
    Output("modal-simple", "opened", allow_duplicate=True),
    Trigger("add-budget-btn", "n_clicks"),
    prevent_initial_call=True
)
def open_modal():
    return None, True


@app.callback(
    Output("modal-simple", "opened", allow_duplicate=True),
    Output("selected-budget", "data", allow_duplicate=True),
    Trigger("modal-close-button", "n_clicks"),
    Trigger("modal-submit-button", "n_clicks"),
    State("selected-budget", "data"),
    State("budget-name", "value"),
    State("copy-select", "value"),
    prevent_initial_call=True
)
def modal_demo(selected, budget_name, copy_from):

    t = get_triggered()
    if t.id == "modal-submit-button":
        if copy_from is not None:
            idx = repo.copy_budget(copy_from, budget_name)
        else:
            idx = repo.create_budget(budget_name)
    else:
        idx = selected

    return False, idx


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='change-store', data={}, storage_type='memory'),
    dcc.Store(id='selected-budget', data=0, storage_type='memory'),
    dcc.Store(id='dirty', data=[], storage_type='memory'),
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
                        ),
                        dmc.Modal(
                            title="Create new budget",
                            id="modal-simple",
                            zIndex=10000,
                            children=[
                                dmc.TextInput(
                                    label="Budget name",
                                    id="budget-name"
                                ),
                                dmc.Select(
                                    label="Copy from...",
                                    placeholder="Select one",
                                    id="copy-select",
                                    value=None,
                                    data=[
                                        {"value": idx, "label": budget.name}
                                        for idx, budget in enumerate(repo.budgets)
                                    ],
                                ),
                                dmc.Space(h=20),
                                dmc.Group(
                                    [
                                        dmc.Button("Submit", id="modal-submit-button"),
                                        dmc.Button(
                                            "Close",
                                            color="red",
                                            variant="outline",
                                            id="modal-close-button",
                                        ),
                                    ],
                                    position="right",
                                ),
                            ],
                        )
                    ]
                )
            ], span=2),
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
                        dmc.TabsPanel(bp.embed(app), value="accounts")
                    ],
                    value="expenses",
                    m="sm"
                )
            ], span=6),
            dmc.Col([
                dmc.Container([
                    balance_summary_bp.embed(app)
                ], m="sm"),
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
                            dmc.TabsPanel(expense_income_graph.bp.embed(app), value="overview"),
                            dmc.TabsPanel(saldo_graph.init(app), value="saldo"),
                            dmc.TabsPanel(movements.init(app), value="movements")
                        ],
                        value="saldo",
                        m="sm"
                    ),
                ])
            ], span=4)
        ])
    ], style=dict(height="calc(100vh - 50px)"))
])

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    app.run_server(
        debug=True
    )
