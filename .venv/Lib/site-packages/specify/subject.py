from prophepy import Mock
from .builtin_matchers import get_matcher
from .exceptions import CustomMatcherError
from .utils import map_for_dict, reveal_if_needed

class Subject:
    '''
    This class represents the specced object.
    '''
    def __init__(self, value, object_behavior):
        '''
        It is instanciated with the real object, and the spec
        '''
        self.__value = value
        self.__object_behavior = object_behavior

    def _get_value(self):
        '''
        Get the real specced object
        '''
        return self.__value

    def match_with_custom_matcher(self, matcher_name, matcher, *args):
        '''
        Launch a test against a custom matcher and raise a CustomMatcherError
        if it fails
        '''
        if not matcher(self.__value, *args):
            raise CustomMatcherError(f'Custom matcher "{matcher_name}" failed.')

        return self.__value

    def __getattr__(self, attr_name):
        '''
        If the method is a _should_ one, it will try to find a matcher
        (builtin or custom one). If not, it will executes the action
        on the internal specced object and return a new Subject instance.
        '''
        if attr_name.startswith('_should_'):
            matcher_type = attr_name[len('_should_'):]

            # custom matcher
            if matcher_type in self.__object_behavior._matchers().keys():
                matcher = self.__object_behavior._matchers()[matcher_type]
                def custom_matcher_wrapper(*args):
                    return Subject(
                        self.match_with_custom_matcher(matcher_type, matcher, *args),
                        self.__object_behavior
                    )
                return custom_matcher_wrapper

            # builtin matcher
            matcher = get_matcher(matcher_type)
            def checker_wrapper(expected_value):
                matcher(self.__value, expected_value)
                return Subject(
                    self.__value,
                    self.__object_behavior
                )
            return checker_wrapper

        def action_wrapper(*args, **kwargs):
            args = map(reveal_if_needed, args)
            kwargs = map_for_dict(reveal_if_needed, kwargs)

            return Subject(
                getattr(self.__value, attr_name)(*args, **kwargs),
                self.__object_behavior
            )

        return action_wrapper
