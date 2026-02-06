from importlib import import_module
import re

def get_spec(path):
    if not path.endswith('_spec.py'):
        return None

    with open(path, 'r') as file:
        content = file.read()
        result = re.search(r"class\s+(?P<class_name>\w+)\(ObjectBehavior\):", content)
        if result is None:
            return None

        class_name = result.group('class_name')
        path = path.rstrip('.py')
        path = path.replace('/', '.')
        path = path.replace('\\', '.')

        module = import_module(path)
        class_obj = getattr(module, class_name)

        return class_obj
