from dataclasses import asdict

from dash.exceptions import PreventUpdate
from dash_extensions.snippets import get_triggered

from finance.model.entry import Budget, EntryGroup, Entry, Account

from dash_extensions.enrich import html, Output, DashProxy, Trigger, State, Input, ALL
import dash_mantine_components as dmc
from dash_extensions.enrich import dash_table

from finance.webapp.helpers import handle_update, create_add_btn
from finance.webapp.modal_input import ModalInput
from finance.webapp.models import ChangeStoreModel
from finance.webapp.state import repo, BudgetNotFoundError


def create_data_table_data(entry_group: EntryGroup):
    data = []
    for x in entry_group.entries:
        _e = asdict(x)
        _e["monthly"] = f"{x.monthly():0.2f}"
        if _e["payment_period"] == 1:
            _e["first_payment_month"] = 0
        data.append(_e)
    return data


def create_data_table(entry_group: EntryGroup, accounts: list[Account]):
    columns = [
        {'id': 'name', 'name': 'Navn', 'type': 'text'},
        {'id': 'owner', 'name': 'Ejer', 'type': 'text'},
        {'id': 'payment_size', 'name': 'Beløb', 'type': 'numeric'},
        {'id': 'payment_period', 'name': 'Frekvens', 'presentation': 'dropdown', 'type': 'text'},
        {'id': 'first_payment_month', 'name': 'Forfald', 'presentation': 'dropdown', 'type': 'text'},
        {'id': 'payment_method', 'name': 'Betalingsmåde', 'presentation': 'dropdown', 'type': 'text'},
        {'id': 'account', 'name': 'Konto', 'presentation': 'dropdown', 'type': 'text'},
        {'id': 'monthly', 'name': 'Månedligt', "editable": False}
    ]

    return dash_table.DataTable(
        id={'type': 'expense-table', 'grp': entry_group.id},
        data=create_data_table_data(entry_group),
        columns=columns,
        editable=True,
        row_deletable=True,
        style_cell_conditional=[
            {
                'if': {'column_type': 'text'},
                'textAlign': 'left'
            },

        ],
        style_data_conditional=[
            {
                'if': {
                    'column_id': 'payment_period',
                    'filter_query': '{payment_period} eq 1'
                },
                'cell_selectable': False
            }
        ],
        dropdown={
            'account': {
                'clearable': False,
                'options': [
                    {'label': acc.name, 'value': acc.name}
                    for acc in accounts
                ]
            },
            'payment_period': {
                'clearable': False,
                'options': [
                    {"value": 1, "label": "Månedsvis"},
                    {"value": 3, "label": "Kvartalsvis"},
                    {"value": 6, "label": "Halvårlig"},
                    {"value": 12, "label": "Årlig"}
                ]
            },
            'first_payment_month': {
                'clearable': False,
                'options': [
                    {"value": x, "label": y} for x, y in enumerate(
                        ["", "Januar", "Februar", "Marts", "April", "Maj", "Juni", "Juli",
                         "August", "September", "Oktober", "November", "December"]
                    )
                ]
            },
            'payment_method': {
                'clearable': False,
                'options': [
                    {"value": x, "label": x} for x in ["BS", "Kort", "MobilePay", "Overførsel"]
                ]
            }
        }
    )


def create_table(budget: Budget):

    children = []
    for entry_group in budget.expenses:
        children.append(
            dmc.AccordionItem([
                dmc.AccordionControl(
                    [
                        dmc.Grid([
                            dmc.Col([dmc.Text(entry_group.name)], span=8),
                            dmc.Col(dmc.Text(f"{entry_group.total_monthly():0.2f}", align="right"), span=4)
                        ])
                    ]
                ),
                dmc.AccordionPanel([
                    dmc.Group([
                        dmc.Button(
                            "Tilføj", id=dict(type="add-expense", grp=entry_group.id),
                            size="xs", mb="5px", variant="outline"
                        ),
                        dmc.Button("Omdøb", id=dict(type="rename-expense", grp=entry_group.id), size="xs", mb="5px", variant="outline", color="green"),
                        dmc.Button("Delete", id=dict(type="delete-expense", grp=entry_group.id), size="xs", mb="5px",
                                   variant="outline", color="red")
                    ], position="right"),
                    create_data_table(entry_group, budget.accounts),
                ])
            ], value=entry_group.id)
        )

    return children


def create_callbacks(app: DashProxy):

    @app.callback(
        Output('change-store', 'data', allow_duplicate=True),
        Trigger(dict(type="delete-expense", grp=ALL), 'n_clicks'),
        State('selected-budget', 'data')
    )
    def delete_expense_grp(budget_idx: str):

        t = get_triggered()
        if t.id is None or t.n_clicks is None:
            raise PreventUpdate()
        entry_grp_id = t.id['grp']
        try:
            budget = repo.get_budget(budget_idx)
            idx = next(i for i in range(0, len(budget.expenses)) if budget.expenses[i].id == entry_grp_id)
            budget.expenses.pop(idx)

            return ChangeStoreModel(budget_idx)
        except BudgetNotFoundError:
            raise PreventUpdate()

    @app.callback(
        Output('change-store', 'data', allow_duplicate=True),
        Input('add-expense-group', 'n_clicks'),
        State('selected-budget', 'data'),
        prevent_initial_call=True
    )
    def add_expense_grp(n_clicks: int, budget_idx: str):
        if n_clicks is None:
            raise PreventUpdate()
        try:
            budget = repo.get_budget(budget_idx)
            budget.expenses.append(EntryGroup(name=f"New group"))
            return ChangeStoreModel(budget_idx)
        except BudgetNotFoundError:
            raise PreventUpdate()

    @app.callback(
        Output('change-store', 'data', allow_duplicate=True),
        Trigger(dict(type='expense-table', grp=ALL), 'data'),
        Trigger(dict(type='expense-table', grp=ALL), 'data_previous'),
        State('selected-budget', 'data'),
        prevent_initial_call=True
    )
    def update_graphs(budget_idx: str) -> ChangeStoreModel:

        t = get_triggered()
        if t.id is None:
            raise PreventUpdate()

        entry_grp_id = t.id['grp']
        try:
            entry_group = next(x for x in repo.get_budget(budget_idx).expenses if x.id == entry_grp_id)
        except (StopIteration, BudgetNotFoundError):
            raise PreventUpdate()

        entries = entry_group.entries

        new_data = t.data
        old_data = t.data_previous

        if new_data and old_data and new_data != old_data:
            handle_update(old_data, new_data, entries, entry_group.name)
            return ChangeStoreModel(budget_idx)
        else:
            raise PreventUpdate()

    @app.callback(
        Output('expense-accordion', 'children'),
        Output('expense-accordion', 'value'),
        Trigger(dict(type='add-expense', grp=ALL), 'n_clicks'),
        Trigger('change-store', 'data'),
        Input('selected-budget', 'data'),
        State('expense-accordion', 'value')
    )
    def update_graphs(budget_idx: str, selected):
        t = get_triggered()
        try:
            budget = repo.get_budget(budget_idx)
        except BudgetNotFoundError:
            raise PreventUpdate()

        if isinstance(t.id, dict) and t.id['type'] == 'add-expense':
            grp = budget.expense_grp_from_id(t.id['grp'])
            grp.entries.append(Entry("New entry...", 0, 1, 1, 0, "BS", budget.accounts[0].name if budget.accounts else "Default", "", ""))

        return create_table(budget), selected


def init(app: DashProxy):

    modal = ModalInput(dict(type="rename-expense", grp=ALL), "Omdøb")

    @modal.modal_callback(
        Output('change-store', 'data', allow_duplicate=True),
        State('selected-budget', 'data')
    )
    def on_modal_input(value, who, budget_idx: str):
        try:
            budget = repo.get_budget(budget_idx)
            expense_grp = budget.expense_grp_from_id(who['grp'])

            expense_grp.name = value

            return ChangeStoreModel(budget_idx)
        except BudgetNotFoundError:
            raise PreventUpdate()

    create_callbacks(app)
    return html.Div([
        modal.embed(app),
        dmc.Accordion(
            id='expense-accordion',
            chevronPosition="left"
        ),
        create_add_btn('add-expense-group')
    ])
