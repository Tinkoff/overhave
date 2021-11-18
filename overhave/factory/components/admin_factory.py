import abc
from functools import cached_property
from multiprocessing.pool import ThreadPool
from typing import Callable, Mapping

from overhave.authorization import (
    AuthorizationStrategy,
    DefaultAdminAuthorizationManager,
    IAdminAuthorizationManager,
    LDAPAdminAuthorizationManager,
    LDAPAuthenticator,
    SimpleAdminAuthorizationManager,
)
from overhave.entities import ReportManager
from overhave.factory.base_factory import IOverhaveFactory
from overhave.factory.components.s3_init_factory import FactoryWithS3ManagerInit
from overhave.factory.context import OverhaveAdminContext
from overhave.storage import IFeatureTypeStorage, SystemUserGroupStorage
from overhave.transport import EmulationTask, PublicationTask, RedisProducer, RedisStream, TestRunTask


class IAdminFactory(IOverhaveFactory[OverhaveAdminContext]):
    """Factory interface for Overhave admin application."""

    @property
    @abc.abstractmethod
    def feature_type_storage(self) -> IFeatureTypeStorage:
        pass

    @property
    @abc.abstractmethod
    def auth_manager(self) -> IAdminAuthorizationManager:
        pass

    @property
    @abc.abstractmethod
    def redis_producer(self) -> RedisProducer:
        pass

    @property
    @abc.abstractmethod
    def report_manager(self) -> ReportManager:
        pass

    @property
    @abc.abstractmethod
    def threadpool(self) -> ThreadPool:
        pass


class AdminFactory(FactoryWithS3ManagerInit[OverhaveAdminContext], IAdminFactory):
    """Factory for Overhave admin application."""

    context_cls = OverhaveAdminContext

    @cached_property
    def _simple_auth_manager(self) -> SimpleAdminAuthorizationManager:
        return SimpleAdminAuthorizationManager(
            settings=self.context.auth_settings, system_user_storage=self._system_user_storage
        )

    @cached_property
    def _default_auth_manager(self) -> DefaultAdminAuthorizationManager:
        return DefaultAdminAuthorizationManager(
            settings=self.context.auth_settings, system_user_storage=self._system_user_storage
        )

    @cached_property
    def _ldap_auth_manager(self) -> LDAPAdminAuthorizationManager:
        return LDAPAdminAuthorizationManager(
            settings=self.context.auth_settings,
            system_user_storage=self._system_user_storage,
            system_user_group_storage=SystemUserGroupStorage(),
            ldap_authenticator=LDAPAuthenticator(settings=self.context.ldap_client_settings),
        )

    @cached_property
    def _auth_manager_mapping(self) -> Mapping[AuthorizationStrategy, Callable[[], IAdminAuthorizationManager]]:
        return {
            AuthorizationStrategy.SIMPLE: lambda: self._simple_auth_manager,
            AuthorizationStrategy.DEFAULT: lambda: self._default_auth_manager,
            AuthorizationStrategy.LDAP: lambda: self._ldap_auth_manager,
        }

    @property
    def auth_manager(self) -> IAdminAuthorizationManager:
        return self._auth_manager_mapping[self.context.auth_settings.auth_strategy]()

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

    @cached_property
    def _threadpool(self) -> ThreadPool:
        if self.context.admin_settings.consumer_based:
            raise RuntimeError("No threadpool when it's a consumer-based application!")
        return ThreadPool(processes=self.context.admin_settings.threadpool_process_num)

    @property
    def threadpool(self) -> ThreadPool:
        return self._threadpool
