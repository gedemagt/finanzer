import uuid
from typing import Any

from dash.exceptions import PreventUpdate
from dash_extensions.enrich import html, Input, Output, State, DashBlueprint, Trigger

import dash_mantine_components as dmc
from dash import dcc
from dash_extensions.snippets import get_triggered


class ModalInput(DashBlueprint):

    def __init__(self, _id: Any, title: str):
        super().__init__()

        self._id = _id
        self._modal_id = str(uuid.uuid4())
        self._submit_id = str(uuid.uuid4())
        self._close_id = str(uuid.uuid4())
        self._store_id_1 = str(uuid.uuid4())
        self._store_id_2 = str(uuid.uuid4())
        self._input_id = str(uuid.uuid4())

        self.layout = html.Div(
            [
                dcc.Store(id=self._store_id_1),
                dcc.Store(id=self._store_id_2),
                dmc.Modal(
                    title=title,
                    id=self._modal_id,
                    zIndex=10000,
                    children=[
                        dmc.TextInput(id=self._input_id),
                        dmc.Space(h=20),
                        dmc.Group(
                            [
                                dmc.Button("Submit", id=self._submit_id),
                                dmc.Button(
                                    "Close",
                                    color="red",
                                    variant="outline",
                                    id=self._close_id,
                                ),
                            ],
                            position="right",
                        ),
                    ],
                ),
            ]
        )

        @self.callback(
            Output(self._store_id_1, "data"),
            Input(self._id, "n_clicks")
        )
        def save_who_clicked(n_clicked):
            if n_clicked is None:
                raise PreventUpdate()
            return get_triggered().id

        @self.callback(
            Output(self._modal_id, "opened"),
            Trigger(self._id, "n_clicks"),
            Trigger(self._close_id, "n_clicks"),
            Trigger(self._submit_id, "n_clicks"),
            prevent_initial_call=True
        )
        def handle_modal_click():

            if get_triggered().n_clicks is None:
                raise PreventUpdate()

            if get_triggered().id == self._close_id:
                return False
            elif get_triggered().id == self._submit_id:
                return False
            else:
                return True

    def modal_callback(self, *args, **kwargs):

        def wrapper(f):
            _args = [
                Input(self._submit_id, "n_clicks"),
                State(self._store_id_1, "data"),
                State(self._input_id, "value")
            ] + list(args)

            @self.callback(
                *_args,
                prevent_initial_call=True
            )
            def john(nc, who_clicked, value, *rest_args):
                if nc is not None:
                    r = f(value, who_clicked, *rest_args)
                    return r
                raise PreventUpdate()

            return f

        return wrapper
