import dataclasses
import inspect

from dash_extensions.enrich import DashTransform
from dataclass_wizard import fromdict, asdict


class _DataclassFunctionWrapper:

    def __init__(self, f, multi_output: bool):
        self.f = f
        self.full_arg_spec = inspect.getfullargspec(self.f)
        self.multi_output = multi_output

        # Identify the indices of the arguments to be converted
        self._args_to_covert = {}
        arg_annotations = self.full_arg_spec.annotations
        for idx, arg_name in enumerate(self.full_arg_spec.args):
            try:
                if dataclasses.is_dataclass(arg_annotations[arg_name]):
                    self._args_to_covert[idx] = arg_annotations[arg_name]
            except KeyError:
                pass

    @staticmethod
    def _convert_arg(obj):
        return asdict(obj) if dataclasses.is_dataclass(obj) else obj

    def __call__(self, *args, **kwargs):

        if not self._args_to_covert:
            result = self.f(*args, **kwargs)
        else:
            new_args = []

            for idx in range(len(args)):
                try:
                    new_args.append(fromdict(self._args_to_covert[idx], args[idx]))
                except KeyError:
                    new_args.append(args[idx])
            result = self.f(*new_args, **kwargs)

        # Always convert the result if it is a dataclass - also in with multiple outputs
        if self.multi_output:
            return [self._convert_arg(x) for x in result]
        else:
            return self._convert_arg(result)


class DataclassTransform(DashTransform):

    def __init__(self):
        super().__init__()

    def apply_serverside(self, callbacks):
        for cb in callbacks:
            cb.f = _DataclassFunctionWrapper(cb.f, cb.multi_output)

        return callbacks
