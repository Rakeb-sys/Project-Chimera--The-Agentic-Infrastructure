from prophepy import Mock

def map_for_dict(func, dictionary):
    return {k: func(v) for k, v in dictionary.items()}

def reveal_if_needed(value):
    if isinstance(value, Mock):
        return value._reveal()

    return value
