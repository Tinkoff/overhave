from overhave.factory.base_factory import OverhaveBaseFactory


class ProxyFactory(OverhaveBaseFactory):
    """ Factory for application entities resolution and usage, based on proxy-object pattern.

    Class inherits :class:`OverhaveBaseFactory` and realise logic for dynamic entities resolution before and
    during application or tests start-up. In fact, it is a proxy-object for :class:`OverhaveBaseFactory`.
    """

    def __init__(self) -> None:
        super().__init__()
        self._pytest_patched = False
        self._collection_prepared = False

    def patch_pytest(self) -> None:
        if not self._pytest_patched:
            self.injector.patch_pytestbdd_prefixes(custom_step_prefixes=self.context.language_settings.step_prefixes)
            self._pytest_patched = True

    @property
    def pytest_patched(self) -> bool:
        return self._pytest_patched

    def supply_injector_for_collection(self) -> None:
        if not self._collection_prepared:
            self.injector.supplement_on_fly(
                project_settings=self.context.project_settings,
                file_settings=self.context.file_settings,
                step_collector=self.step_collector,
                test_runner=self.test_runner,
                feature_types=self.feature_extractor.feature_types,
            )
            self._collection_prepared = True
