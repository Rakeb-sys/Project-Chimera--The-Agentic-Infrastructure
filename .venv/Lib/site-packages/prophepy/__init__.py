from importlib import import_module
from .exceptions import UndefinedMockBehaviorError, MethodWasNotCalledError

class AttributeProphecy:
    '''
    This is the return of every call to the mock object
    (You can then do a _will_return(…) or _should_be_called() on it)
    '''
    def __init__(self, mock, name, args, kwargs):
        '''
        Takes the parent mock, the name of the method and the args
        '''
        self.mock = mock
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self.called_times = 0

    def _will_return(self, value):
        '''
        Create the behavior of the method
        '''
        self.return_value = value
        self.mock.add_prophecy(self)

        return self

    def _should_be_called(self):
        '''
        Add this method call to the expected ones
        '''
        self.mock.should_call_prophecy(self)
        self.mock.add_prophecy(self)

    def __str__(self) -> str:
        '''
        Make the attribute prophecy easy to read for debug in exceptions
        '''
        args = [str(arg) for arg in self.args]
        kwargs = [str(kwarg) for kwarg in self.kwargs]

        return f"{self.name}, args: {args}, kwargs: {kwargs}"

class Mock():
    '''
    This mock class is used to drive the behavior of the object.
    When we want to access the real object besides, we use mock.reveal().
    '''
    def __init__(self, mocked_object_cls):
        '''
        Instanciates the mocked object based on the given class
        '''
        self.__mock_object = mocked_object_cls.__new__(mocked_object_cls)
        self.__mock_object._prophecies = []
        self.__mock_object._prophecies_to_call = []
    pass

    def add_prophecy(self, attribute_prophecy: AttributeProphecy):
        '''
        Add a prophecy to the list of the mocked object
        '''
        self.__mock_object._prophecies.append(attribute_prophecy)

    def _get_existing_prophecy(self, name, args, kwargs):
        '''
        Avoid creating new prophecy if a similar exists already
        (example running twice `mock.add(2, 3)`),
        in the case of _should_be_called() and _will_return(5)
        '''
        for prophecy in self.__mock_object._prophecies:
            if name == prophecy.name and args == prophecy.args and kwargs == prophecy.kwargs:
                return prophecy

        return None

    def should_call_prophecy(self, attribute_prophecy: AttributeProphecy):
        '''
        Add the prophecy to the list of expected calls
        '''
        self.__mock_object._prophecies_to_call.append(attribute_prophecy)

    def check_prophecies(self):
        '''
        Check in the end if everything happened as Nostradamus said
        '''
        for prophecy in self.__mock_object._prophecies_to_call:
            if prophecy.called_times == 0:
                raise MethodWasNotCalledError(f"Method {str(prophecy)} should have been called but was not.")

    def _reveal(self):
        '''
        Get the mocked object
        '''
        return self.__mock_object

    def __getattr__(self, attr_name):
        '''
        Returns an AttributeProphecy when a method is called.
        An existing one if there is one, or a new one.
        '''
        def wrapper(*args, **kwargs):
            existing_prophecy = self._get_existing_prophecy(
                attr_name,
                args,
                kwargs
            )

            if None == existing_prophecy:
                return AttributeProphecy(self, attr_name, args, kwargs)

            return existing_prophecy

        return wrapper

def prophesize(cls):
    '''
    This function takes a class name and returns a Mock object
    '''

    class MockedObject(cls):
        '''
        The mocked object. It extends from the given class.
        You will pass this one to your objects in tests.
        '''
        def __getattribute__(self, attr_name):
            '''
            If it is not a method, we just return the value.
            Otherwise, we use the given behavior for this method,
            and we raise an error if it was not defined.
            '''
            if not callable(cls.__getattribute__(self, attr_name)):
                return cls.__getattribute__(self, attr_name)

            def wrapper(*args, **kwargs):
                for prophecy in self._prophecies:
                    if attr_name == prophecy.name and args == prophecy.args and kwargs == prophecy.kwargs:
                        prophecy.called_times += 1

                        return prophecy.return_value
                raise UndefinedMockBehaviorError('No return value was specified for this call')
            return wrapper
        pass

    return Mock(MockedObject)

class InternalProphesizer:
    def __init__(self, name, value, **kwargs):
        self.from_module = kwargs['from_module']
        self.name = name
        self.value = value

        self.module = import_module(self.from_module)
        self.original_value = getattr(self.module, self.name)
        setattr(self.module, self.name, self.value)

    def leave_clean(self):
        setattr(self.module, self.name, self.original_value)
