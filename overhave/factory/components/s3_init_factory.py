from overhave.factory.base_factory import BaseOverhaveFactory
from overhave.factory.context import TApplicationContext


class FactoryWithS3ManagerInit(BaseOverhaveFactory[TApplicationContext]):
    """ Factory with :class:`S3Manager` initialization. """

    def set_context(self, context: TApplicationContext) -> None:
        super().set_context(context)  # type: ignore
        if not self.context.s3_manager_settings.enabled:
            return
        self._s3_manager.initialize()
