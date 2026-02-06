from typing import List

class ResultLine:
    '''
    A result is made of several result lines
    '''
    def __init__(self, spec_class, test_name, exception=None):
        '''
        Take the spec_class (object_behavior), the test name (it_…),
        and the exception if any
        '''
        self.spec_class = spec_class
        self.test_name = test_name
        self.exception = exception

class Result:
    '''
    The final Result object that will contain the whole results
    '''
    def __init__(self, result_lines: List[ResultLine]):
        self.result_lines = result_lines

    def _prettify_test_name(self, test_name):
        '''
        "it_works_correctly" becomes "it works correctly"
        '''
        return test_name.replace('_', ' ')

    def _print_line(self, num: int, line: ResultLine):
        '''
        Take an index and a result line, and transform it
        to a valid TAP line ("ok 1 - Test name…")
        '''
        if line.exception is None:
            prefix = 'ok'
        else:
            prefix = 'not ok'

        desc = f"{line.spec_class.__qualname__}: {self._prettify_test_name(line.test_name)}"
        text = f"{prefix} {num} - {desc}"

        if line.exception is not None:
            text = text + "\n    ---"
            text = text + "\n    " + line.exception
            text = text + "\n    ..."

        return text

    def export(self):
        '''
        Export the final output for a valid TAP result
        '''
        text = "TAP version 13\n"
        last_elem = len(self.result_lines)
        text = text + f"1..{last_elem}\n"

        for index, line in enumerate(self.result_lines):
            text = text + "\n" + self._print_line(index+1, line)

        return text
