import abc
from functools import cached_property
from typing import Any, Dict

from overhave.entities import ReportManager
from overhave.entities.authorization import AuthorizationStrategy, IAdminAuthorizationManager, LDAPAuthenticator
from overhave.entities.authorization.mapping import AUTH_STRATEGY_TO_MANAGER_MAPPING
from overhave.factory.base_factory import BaseOverhaveFactory, IOverhaveFactory
from overhave.factory.context import OverhaveAdminContext
from overhave.storage import IFeatureTypeStorage
from overhave.transport import EmulationTask, PublicationTask, RedisProducer, RedisStream, TestRunTask


class IAdminFactory(IOverhaveFactory[OverhaveAdminContext]):
    """ Factory interface for Overhave admin application. """

    context_cls = OverhaveAdminContext

    @property
    @abc.abstractmethod
    def auth_manager(self) -> IAdminAuthorizationManager:
        pass

    @property
    @abc.abstractmethod
    def feature_type_storage(self) -> IFeatureTypeStorage:
        pass

    @property
    @abc.abstractmethod
    def redis_producer(self) -> RedisProducer:
        pass

    @property
    @abc.abstractmethod
    def report_manager(self) -> ReportManager:
        pass


class AdminFactory(BaseOverhaveFactory[OverhaveAdminContext], IAdminFactory):
    """ Factory for Overhave admin application. """

    @cached_property
    def _auth_manager(self) -> IAdminAuthorizationManager:
        settings = self.context.auth_settings
        kwargs: Dict[str, Any] = dict(settings=settings)
        if settings.auth_strategy is AuthorizationStrategy.LDAP:
            kwargs["ldap_authenticator"] = LDAPAuthenticator(settings=self.context.ldap_client_settings)
        return AUTH_STRATEGY_TO_MANAGER_MAPPING[settings.auth_strategy](**kwargs)  # type: ignore

    @property
    def auth_manager(self) -> IAdminAuthorizationManager:
        return self._auth_manager

    @property
    def feature_type_storage(self) -> IFeatureTypeStorage:
        return self._feature_type_storage

    @cached_property
    def _redis_producer(self) -> RedisProducer:
        return RedisProducer(
            settings=self.context.redis_settings,
            mapping={
                TestRunTask: RedisStream.TEST,
                PublicationTask: RedisStream.PUBLICATION,
                EmulationTask: RedisStream.EMULATION,
            },
        )

    @property
    def redis_producer(self) -> RedisProducer:
        return self._redis_producer
