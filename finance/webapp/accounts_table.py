from dash.exceptions import PreventUpdate

from finance.model.entry import Budget, AccountType

from dash_extensions.enrich import html, Input, Output, Trigger, State, DashBlueprint
from dash_extensions.enrich import dash_table

from finance.webapp.helpers import handle_update, create_add_btn
from finance.webapp.models import ChangeStoreModel
from finance.webapp.state import repo


bp = DashBlueprint()


def create_data_table_data(budget: Budget):
    expense_balances, income_balances, transfer_balances = budget.calculate_balances()

    data = []
    for account in budget.accounts:
        before = income_balances[account.name] + transfer_balances[account.name]
        after = before + expense_balances[account.name]
        data.append(dict(
            name=account.name,
            owner=account.owner,
            type=account.type,
            before=f"{before:0.2f}",
            after=f"{after:0.2f}"
        ))
    return data


def create_data_table(budget: Budget):
    columns = [
        {'id': 'name', 'name': 'Navn', 'type': 'text'},
        {'id': 'owner', 'name': 'Ejer', 'type': 'text'},
        {'id': 'type', 'name': 'Type', 'presentation': 'dropdown', 'type': 'text'},
        {'id': 'before', 'name': 'Før udgifter', 'type': 'numeric'},
        {'id': 'after', 'name': 'Efter udgifter', 'type': 'numeric'}
    ]

    return dash_table.DataTable(
        id='accounts-table',
        data=create_data_table_data(budget),
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
            'type': {
                'clearable': False,
                'options': [
                    {'label': acc_type.value, 'value': acc_type.value}
                    for acc_type in AccountType
                ]
            }
        }
    )


@bp.callback(
    Output('change-store', 'data', allow_duplicate=True),
    Input('accounts-table', 'data'),
    Input('accounts-table', 'data_previous'),
    State('selected-budget', 'data'),
    prevent_initial_call=True
)
def update_graphs(data: dict, data_previous: dict, budget_idx: str) -> ChangeStoreModel:
    budget = repo.get_budget(budget_idx)
    if data and data_previous and data != data_previous:
        handle_update(data_previous, data, budget.transfers, "Accounts")
        return ChangeStoreModel(budget_idx)
    else:
        raise PreventUpdate()


@bp.callback(
    Output('accounts', 'children'),
    Input('selected-budget', 'data'),
    Trigger('change-store', 'data')
)
def update(budget_idx: str):
    budget = repo.get_budget(budget_idx)
    return [
        create_data_table(budget),
        create_add_btn("add-transfer")
    ]


bp.layout = html.Div(id="accounts")
