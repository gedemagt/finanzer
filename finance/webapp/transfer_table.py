from dataclasses import asdict
from uuid import uuid4

from dash.exceptions import PreventUpdate

from finance.model.entry import Budget

from dash_extensions.enrich import html, Input, Output, DashProxy, Trigger
from dash_extensions.enrich import dash_table

from finance.webapp.helpers import handle_update, create_add_btn
from finance.webapp.state import get_budget


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
        prevent_initial_call=True
    )
    def update_graphs(data, data_previous):

        budget = get_budget()

        if data and data_previous and data != data_previous:
            handle_update(data_previous, data, budget.transfers, "Transfers")

            return str(uuid4())
        else:
            raise PreventUpdate()

    @app.callback(
        Output('transfers', 'children'),
        Input('selected-budget', 'data'),
        Trigger('change-store', 'data')
    )
    def update(budget_idx: int):
        budget = get_budget(budget_idx)
        return [
            create_data_table(budget),
            create_add_btn("add-transfer")
        ]


def init(app: DashProxy):
    create_callbacks(app)
    return html.Div(id="transfers")
