import abc

import werkzeug

from overhave.transport import TestRunTask


class IProcessor(abc.ABC):
    """ Abstract class for application processor. """

    @abc.abstractmethod
    def execute_test(self, task: TestRunTask) -> None:
        pass

    @abc.abstractmethod
    def create_version(self, test_run_id: int, published_by: str) -> werkzeug.Response:
        pass
