from .exceptions import MatcherError, MatcherNotFoundError

def be(value, expected):
    if value is not expected:
        raise MatcherError(f"Expected {value} to be {expected}")

def be_like(value, expected):
    if value != expected:
        raise MatcherError(f"Expected {value} to be like {expected}")

def not_be(value, not_expected):
    if value is not_expected:
        raise MatcherError(f"Expected {value} not to be {not_expected}")

def not_be_like(value, not_expected):
    if value == not_expected:
        raise MatcherError(f"Expected {value} not to be like {not_expected}")

def be_an_instance_of(value, cls):
    if not isinstance(value, cls):
        raise MatcherError(f"Expected {value} to be an instance of {cls.__qualname__}, got {type(value)}")

def have_length(value, length):
    if len(value) != length:
        raise MatcherError(f"Expected value length to be {length} but length is {len(value)}")

def get_matcher(type):
    items = {
        'be': be,
        'not_be': not_be,
        'return': be,
        'not_return': not_be,
        'be_like': be_like,
        'not_be_like': not_be_like,
        'return_like': be_like,
        'not_return_like': not_be_like,
        'be_an_instance_of': be_an_instance_of,
        'return_an_instance_of': be_an_instance_of,
        'have_length': have_length
    }

    if type not in items:
        raise MatcherNotFoundError(f'No builtin matcher exists with type "{type}"')

    return items[type]
