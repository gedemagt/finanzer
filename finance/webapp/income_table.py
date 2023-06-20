from dataclasses import asdict

from dash import ALL
from dash.exceptions import PreventUpdate
from dash_extensions.snippets import get_triggered

from finance.model.entry import Budget, EntryGroup, Entry

from dash_extensions.enrich import html, Output, DashProxy, Trigger, Input, State
import dash_mantine_components as dmc
from dash_extensions.enrich import dash_table

from finance.webapp.helpers import handle_update, create_add_btn
from finance.webapp.modal_input import ModalInput
from finance.webapp.models import ChangeStoreModel
from finance.webapp.state import repo


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
        id={'type': 'incomes-table', 'grp': entry_group.id},
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
                    dmc.Group([

                        dmc.Button("Omdøb", id=dict(type="rename-income", grp=entry_group.id), size="xs", mb="5px", variant="outline", color="green"),
                        dmc.Button("Delete", id=dict(type="delete-income", grp=entry_group.id), size="xs", mb="5px",
                                   variant="outline", color="red")
                    ], position="right"),
                    create_data_table(entry_group, budget),
                    create_add_btn(dict(type="add-income", grp=entry_group.id))
                ])
            ], value=entry_group.id)
        )

    return children


def create_callbacks(app: DashProxy):

    @app.callback(
        Output('change-store', 'data', allow_duplicate=True),
        Trigger(dict(type="delete-income", grp=ALL), 'n_clicks'),
        State('selected-budget', 'data')
    )
    def delete_income_group(budget_idx: int):

        t = get_triggered()
        if t.id is None or t.n_clicks is None:
            raise PreventUpdate()
        entry_grp_id = t.id['grp']

        budget = repo.get_budget(budget_idx)
        idx = next(i for i in range(0, len(budget.incomes)) if budget.incomes[i].id == entry_grp_name)
        budget.incomes.pop(idx)

        return ChangeStoreModel(budget_idx)

    @app.callback(
        Output('change-store', 'data', allow_duplicate=True),
        Input('add-income-group', 'n_clicks'),
        State('selected-budget', 'data'),
        prevent_initial_call=True
    )
    def add_income_grp(n_clicks: int, budget_idx: int):
        if n_clicks is None:
            raise PreventUpdate()
        budget = repo.get_budget(budget_idx)
        budget.incomes.append(EntryGroup(name=f"New group"))
        return ChangeStoreModel(budget_idx)

    @app.callback(
        Output('change-store', 'data', allow_duplicate=True),
        Trigger(dict(type='income-table', grp=ALL), 'data'),
        Trigger(dict(type='income-table', grp=ALL), 'data_previous'),
        State('selected-budget', 'data'),
        prevent_initial_call=True
    )
    def update_graphs(budget_idx: int) -> ChangeStoreModel:

        t = get_triggered()
        if t.id is None:
            raise PreventUpdate()

        entry_grp_id = t.id['grp']
        try:
            entry_group = next(x for x in repo.get_budget(budget_idx).incomes if x.id == entry_grp_id)
        except StopIteration:
            raise PreventUpdate()

        entries = entry_group.entries

        new_data = t.data
        old_data = t.data_previous

        if new_data and old_data and new_data != old_data:
            handle_update(old_data, new_data, entries, entry_grp_id)
            return ChangeStoreModel(budget_idx)
        else:
            raise PreventUpdate()

    @app.callback(
        Output('income-accordion', 'children'),
        Output('income-accordion', 'value'),
        Trigger(dict(type='add-income', grp=ALL), 'n_clicks'),
        Trigger('change-store', 'data'),
        Input('selected-budget', 'data'),
        State('expense-accordion', 'value')
    )
    def update_graphs(budget_idx: int, selected):

        t = get_triggered()
        budget = repo.get_budget(budget_idx)

        if isinstance(t.id, dict) and t.id['type'] == 'add-income':
            entry_grp_id = t.id['grp']
            grp = next(x for x in budget.incomes if x.id == entry_grp_id)
            grp.entries.append(Entry("New entry...", 0, 1, 1, 0, "BS", budget.accounts[0].name, "", ""))

        return create_table(budget), selected


def init(app: DashProxy):

    modal = ModalInput(dict(type="rename-income", grp=ALL), "Omdøb")

    @modal.modal_callback(
        Output('change-store', 'data', allow_duplicate=True),
        State('selected-budget', 'data')
    )
    def on_modal_input(value, who, budget_idx: int):
        budget = repo.get_budget(budget_idx)
        income_grp = next(x for x in budget.incomes if x.id == who['grp'])

        income_grp.name = value

        return ChangeStoreModel()

    create_callbacks(app)
    return html.Div([
        modal.embed(app),
        dmc.Accordion(
            id='income-accordion',
            chevronPosition="left"
        ),
        create_add_btn('add-income-group')
    ])
