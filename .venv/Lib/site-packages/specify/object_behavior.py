from prophepy import Mock
from .subject import Subject
from .utils import reveal_if_needed, map_for_dict

class ObjectBehavior:
    '''
    This is the class used as parent for every spec.
    '''
    def __init__(self):
        self._mocked_objects = []
        self._mocked_internals = []

    def _describe(self, cls):
        '''
        Needed first to tell specify which class to spec
        '''
        obj = cls.__new__(cls)
        self.__obj = Subject(obj, self)

    def _be_constructed_with(self, *args, **kwargs):
        '''
        Launch the init method on the specced class with the provided arguments
        '''
        revealed_args = map(reveal_if_needed, args)
        revealed_kwargs = map_for_dict(reveal_if_needed, kwargs)
        self.__obj._get_value().__init__(*revealed_args, **revealed_kwargs)

    def _get_wrapped_object(self):
        '''
        Access to the subject (Subject class)
        '''
        return self.__obj

    def __getattr__(self, attr_name):
        '''
        The magic happens here, when it comes to _should_ methods.
        If the method is a _should_ one, it will try to find a
        matcher (a builtin or a custom one).
        Otherwise, it really calls the specced object method,
        and it returns a Subject instance.
        '''
        matcher_prefix = '_should_'

        if attr_name.startswith(matcher_prefix):
            matchers_keys = self.matchers.keys()
            key = attr_name[len(prefix):]
            if key in matchers_keys:
                custom_matcher = self.matchers()[key]
                def custom_matcher_wrapper(*args):
                    return self.__obj.match_with_custom_matcher(
                        key,
                        custom_matcher,
                        *args
                    )
                return custom_matcher_wrapper

        def subject_wrapper(*args, **kwargs):
            return getattr(self.__obj, attr_name)(*args, **kwargs)

        return subject_wrapper

    def _matchers(self):
        '''
        By default, empty dict of custom matchers
        '''
        return {}

    def _let(self):
        '''
        By default, nothing happens before a test, but can be overriden.
        '''
        pass

    def _let_go(self):
        '''
        By default, nothing happens after a test, but can be overriden.
        '''
        pass
