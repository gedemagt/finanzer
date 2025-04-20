from dataclasses import asdict
from dash.exceptions import PreventUpdate
from dash_extensions.snippets import get_triggered

from finance.model.entry import Budget, Transfer

from dash_extensions.enrich import html, Input, Output, DashProxy, Trigger, State
from dash_extensions.enrich import dash_table

from finance.webapp.helpers import handle_update, create_add_btn
from finance.webapp.models import ChangeStoreModel
from finance.webapp.state import repo, BudgetNotFoundError


def create_data_table(budget: Budget):
    columns = [
        {'id': 'name', 'name': 'Navn', 'type': 'text'},
        {'id': 'owner', 'name': 'Ejer', 'type': 'text'},
        {'id': 'source', 'name': 'Fra', 'presentation': 'dropdown', 'type': 'text'},
        {'id': 'destination', 'name': 'Til', 'presentation': 'dropdown', 'type': 'text'},
        {'id': 'amount', 'name': 'Beløb', 'type': 'numeric'}
    ]

    return dash_table.DataTable(
        id='transfer-table',
        data=[asdict(x) for x in budget.transfers],
        columns=columns,
        editable=True,
        style_cell_conditional=[
            {
                'if': {'column_type': 'text'},
                'textAlign': 'left'
            },
            {
                'if': {'column_type': 'text'},
                'textAlign': 'left'
            }
        ],
        dropdown={
            'source': {
                'clearable': False,
                'options': [
                    {'label': acc.name, 'value': acc.name}
                    for acc in budget.accounts
                ]
            },
            'destination': {
                'clearable': False,
                'options': [
                    {'label': acc.name, 'value': acc.name}
                    for acc in budget.accounts
                ]
            }
        }
    )


def create_callbacks(app: DashProxy):

    @app.callback(
        Output('change-store', 'data', allow_duplicate=True),
        Input('transfer-table', 'data'),
        Input('transfer-table', 'data_previous'),
        State('selected-budget', 'data'),
        prevent_initial_call=True
    )
    def update_graphs(data: dict, data_previous: dict, budget_idx: str) -> ChangeStoreModel:
        try:
            budget = repo.get_budget(budget_idx)
        except BudgetNotFoundError:
            raise PreventUpdate()

        if data and data_previous and data != data_previous:
            handle_update(data_previous, data, budget.transfers, "Transfers")

            return ChangeStoreModel(budget_idx)
        else:
            raise PreventUpdate()

    @app.callback(
        Output('transfers', 'children'),
        Input('selected-budget', 'data'),
        Trigger('change-store', 'data')
    )
    def update(budget_idx: str):
        try:
            budget = repo.get_budget(budget_idx)
            return [
                create_data_table(budget),
                create_add_btn("add-transfer")
            ]
        except BudgetNotFoundError:
            raise PreventUpdate()

    @app.callback(
        Output('change-store', 'data', allow_duplicate=True),
        Trigger("add-transfer", "n_clicks"),
        State("selected-budget", "data"),
        prevent_initial_call=True
    )
    def on_new_account(budget_idx: str):
        if get_triggered().n_clicks is None:
            raise PreventUpdate()
        try:
            budget = repo.get_budget(budget_idx)
            budget.add_transfer(Transfer(name="New transfer", amount=0, source=budget.accounts[0].name, destination=budget.accounts[1].name))
            return ChangeStoreModel(budget_idx)
        except BudgetNotFoundError:
            raise PreventUpdate()


def init(app: DashProxy):
    create_callbacks(app)
    return html.Div(id="transfers")
