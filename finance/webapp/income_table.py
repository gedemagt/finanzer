from dataclasses import asdict
from uuid import uuid4

from dash import ALL
from dash.exceptions import PreventUpdate
from dash_extensions.snippets import get_triggered

from finance.model.entry import Budget, EntryGroup, Entry

from dash_extensions.enrich import html, Output, DashProxy, Trigger, Input
import dash_mantine_components as dmc
from dash_extensions.enrich import dash_table

from finance.webapp.helpers import handle_update, create_add_btn
from finance.webapp.state import get_budget


def create_data_table_data(entry_group: EntryGroup):
    data = []
    for x in entry_group.entries:
        _e = asdict(x)
        _e["monthly"] = f"{x.monthly():0.2f}"
        data.append(_e)
    return data


def create_data_table(entry_group: EntryGroup, budget: Budget):
    columns = [
        {'id': 'name', 'name': 'Navn', 'type': 'text'},
        {'id': 'owner', 'name': 'Ejer', 'type': 'text'},
        {'id': 'payment_size', 'name': 'Beløb', 'type': 'numeric'},
        {'id': 'account', 'name': 'Konto', 'presentation': 'dropdown', 'type': 'text'},
        {'id': 'monthly', 'name': 'Månedligt', "editable": False}
    ]

    return dash_table.DataTable(
        id={'type': 'incomes-table', 'grp': entry_group.name},
        data=create_data_table_data(entry_group),
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
            'account': {
                'clearable': False,
                'options': [
                    {'label': acc.name, 'value': acc.name}
                    for acc in budget.accounts
                ]
            }
        }
    )


def create_table(budget: Budget):

    children = []
    for entry_group in budget.incomes:
        children.append(
            dmc.AccordionItem([
                dmc.AccordionControl(
                    [
                        dmc.Grid([
                            dmc.Col(entry_group.name, span=10),
                            dmc.Col(dmc.Text(f"{entry_group.total_monthly():0.2f}", align="right"), span=2)
                        ])
                    ]
                ),
                dmc.AccordionPanel([
                    create_data_table(entry_group, budget),
                    create_add_btn(dict(type="add-income", grp=entry_group.name))
                ])
            ], value=entry_group.name)
        )

    return dmc.Accordion(children=children, chevronPosition="left", value=budget.incomes[0].name if budget.incomes else None)


def create_callbacks(app: DashProxy):

    @app.callback(
        Output('change-store', 'data', allow_duplicate=True),
        Trigger(dict(type='income-table', grp=ALL), 'data'),
        Trigger(dict(type='income-table', grp=ALL), 'data_previous'),
        prevent_initial_call=True
    )
    def update_graphs():

        list_to_act_on = get_budget().incomes

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
        Output('incomes', 'children'),
        Input('selected-budget', 'data'),
        Trigger(dict(type='add-income', grp=ALL), 'n_clicks'),
        Trigger('change-store', 'data'),
        prevent_initial_call=True
    )
    def update_graphs(budget_idx: int):

        t = get_triggered()
        budget = get_budget(budget_idx)
        list_to_act_on = budget.incomes

        if isinstance(t.id, dict) and t.id['type'] == 'add-income':
            entry_grp_name = t.id['grp']
            grp = next(x for x in list_to_act_on if x.name == entry_grp_name)
            grp.entries.append(Entry("New entry...", 0, 1, 1, 0, "BS", budget.accounts[0].name, "", ""))

        return create_table(budget)


def init(app: DashProxy):
    create_callbacks(app)
    return html.Div(id="incomes")