import abc

import werkzeug


class IProcessor(abc.ABC):
    """ Abstract class for application processor. """

    @abc.abstractmethod
    def execute_test(self, test_run_id: int) -> werkzeug.Response:
        pass

    @abc.abstractmethod
    def create_version(self, test_run_id: int, published_by: str) -> werkzeug.Response:
        pass
