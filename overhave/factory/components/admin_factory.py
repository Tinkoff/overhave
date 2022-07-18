import abc
from functools import cached_property, partial
from multiprocessing.pool import ThreadPool
from typing import Callable, Mapping

from overhave.base_settings import AuthorizationStrategy
from overhave.entities import (
    DefaultAdminAuthorizationManager,
    IAdminAuthorizationManager,
    LDAPAdminAuthorizationManager,
    ReportManager,
    SimpleAdminAuthorizationManager,
)
from overhave.factory.base_factory import IOverhaveFactory
from overhave.factory.components.s3_init_factory import FactoryWithS3ManagerInit
from overhave.factory.context import OverhaveAdminContext
from overhave.storage import IFeatureTypeStorage, SystemUserGroupStorage
from overhave.transport import (
    EmulationTask,
    LDAPAuthenticator,
    PublicationTask,
    RedisProducer,
    RedisStream,
    TestRunTask,
)


class IAdminFactory(IOverhaveFactory[OverhaveAdminContext]):
    """Factory interface for Overhave admin application."""

    @property
    @abc.abstractmethod
    def feature_type_storage(self) -> IFeatureTypeStorage:
        pass

    @cached_property
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

    def _get_simple_auth_manager(self) -> partial[SimpleAdminAuthorizationManager]:
        return partial(SimpleAdminAuthorizationManager, system_user_storage=self._system_user_storage)

    def _get_default_auth_manager(self) -> partial[DefaultAdminAuthorizationManager]:
        return partial(DefaultAdminAuthorizationManager, system_user_storage=self._system_user_storage)

    def _get_ldap_auth_manager(self) -> partial[LDAPAdminAuthorizationManager]:
        return partial(
            LDAPAdminAuthorizationManager,
            settings=self.context.ldap_manager_settings,
            system_user_storage=self._system_user_storage,
            system_user_group_storage=SystemUserGroupStorage(),
            ldap_authenticator=LDAPAuthenticator(settings=self.context.ldap_client_settings),
        )

    @property
    def _auth_manager_mapping(
        self,
    ) -> Mapping[AuthorizationStrategy, Callable[[None], partial[IAdminAuthorizationManager]]]:
        return {
            AuthorizationStrategy.SIMPLE: self._get_simple_auth_manager,  # type: ignore
            AuthorizationStrategy.DEFAULT: self._get_default_auth_manager,  # type: ignore
            AuthorizationStrategy.LDAP: self._get_ldap_auth_manager,  # type: ignore
        }

    @cached_property
    def auth_manager(self) -> IAdminAuthorizationManager:
        partial_auth_manager: partial[IAdminAuthorizationManager] = self._auth_manager_mapping[  # type: ignore
            self.context.auth_settings.auth_strategy
        ]()
        return partial_auth_manager()

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
