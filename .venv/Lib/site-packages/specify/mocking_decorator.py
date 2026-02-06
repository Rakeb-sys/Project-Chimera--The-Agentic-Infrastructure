from importlib import import_module
from prophepy import prophesize, InternalProphesizer

def mock(cls):
    def func_wrapper(func):
        mocked_object = prophesize(cls)

        def arg_wrapper(*args):
            self = args[0]
            self._mocked_objects.append(mocked_object)
            return func(*args, mocked_object)

        return arg_wrapper

    return func_wrapper

def mock_internal(module_name, value, **kwargs):
    internal_mock = InternalProphesizer(module_name, value, **kwargs)

    def func_wrapper(func):
        def arg_wrapper(*args):
            self = args[0]
            self._mocked_internals.append(internal_mock)
            return func(*args)

        return arg_wrapper

    return func_wrapper
