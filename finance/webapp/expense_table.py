from dataclasses import asdict
from typing import List
from uuid import uuid4

from dash import ALL
from dash.exceptions import PreventUpdate
from dash_extensions.snippets import get_triggered

from finance.model.entry import Budget, EntryGroup, Entry, Account

from dash_extensions.enrich import html, Output, DashProxy, Trigger
import dash_mantine_components as dmc
from dash_extensions.enrich import dash_table

from finance.webapp.helpers import handle_update, create_add_btn


def create_data_table_data(entry_group: EntryGroup):
    data = []
    for x in entry_group.entries:
        _e = asdict(x)
        _e["monthly"] = f"{x.monthly():0.2f}"
        if _e["payment_period"] == 1:
            _e["first_payment_month"] = 0
        data.append(_e)
    return data


def create_data_table(entry_group: EntryGroup, accounts: List[Account]):
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
        id={'type': 'expense-table', 'grp': entry_group.name},
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
                    create_data_table(entry_group, budget.accounts),
                    create_add_btn(dict(type="add-expense", grp=entry_group.name))
                ])
            ], value=entry_group.name)
        )

    return dmc.Accordion(
        children=children,
        chevronPosition="left"
    )


def create_callbacks(app: DashProxy, budget: Budget):

    list_to_act_on = budget.expenses

    @app.callback(
        Output('change-store', 'data', allow_duplicate=True),
        Trigger(dict(type='expense-table', grp=ALL), 'data'),
        Trigger(dict(type='expense-table', grp=ALL), 'data_previous'),
        prevent_initial_call=True
    )
    def update_graphs():
        t = get_triggered()
        entry_grp_name = t.id['grp']
        try:
            entry_group = next(x for x in list_to_act_on if x.name == entry_grp_name)
        except StopIteration:
            raise PreventUpdate()

        entries = entry_group.entries

        new_data = t.data
        old_data = t.data_previous

        if new_data and old_data and new_data != old_data:
            handle_update(old_data, new_data, entries, entry_grp_name)
            return str(uuid4())
        else:
            raise PreventUpdate()

    @app.callback(
        Output('expenses', 'children'),
        Trigger(dict(type='add-expense', grp=ALL), 'n_clicks'),
        Trigger('save-btn', 'n_clicks'),
        Trigger('change-store', 'data'),
        prevent_initial_call=True
    )
    def update_graphs():

        t = get_triggered()

        if isinstance(t.id, dict) and t.id['type'] == 'add-expense':
            entry_grp_name = t.id['grp']
            grp = next(x for x in list_to_act_on if x.name == entry_grp_name)
            grp.entries.append(Entry("New entry...", 0, 1, 1, 0, "BS", budget.accounts[0].name, "", ""))

        return create_table(budget)


def create_layout(budget: Budget):
    return html.Div(id="expenses", children=[create_table(budget)])


def init(app: DashProxy, budget: Budget):
    create_callbacks(app, budget)
    return create_layout(budget)
