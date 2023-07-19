==========================
 Overhave context example
==========================

.. code-block:: python

    from overhave import (
        OverhaveAdminContext,
        OverhaveAdminSettings,
        OverhaveAuthorizationSettings,
        OverhaveAuthorizationStrategy,
        OverhaveFileSettings,
        OverhaveLanguageSettings,
        OverhaveLdapClientSettings,
        OverhaveLdapManagerSettings,
        OverhaveProjectSettings,
        OverhaveStashClientSettings,
        OverhaveStashPublisherSettings,
    )
    from overhave.extra import RUSSIAN_PREFIXES

    from my_project import MyCustomPathSettings

    path_settings = MyCustomPathSettings()  # it's your settings with paths to project directories

    my_custom_context = OverhaveAdminContext(
        file_settings=OverhaveFileSettings(
            features_dir=path_settings.features_dir,
            fixtures_dir=path_settings.fixtures_dir,
            tmp_dir=path_settings.tmp_dir,
        ),
        language_settings=OverhaveLanguageSettings(step_prefixes=RUSSIAN_PREFIXES),
        project_settings=OverhaveProjectSettings(
            task_tracker_url="https://jira.company.com/browse",
            tasks_keyword="Tasks",
        ),
        admin_settings=OverhaveAdminSettings(
            index_template_path=path_settings.index_template_path,
            support_chat_url="https://messenger.company.com/chat_id",
        ),
        auth_settings=OverhaveAuthorizationSettings(auth_strategy=AuthorizationStrategy.LDAP),
        ldap_client_settings=OverhaveLdapClientSettings(
            ldap_url="ldap://company.com", ldap_domain="company\\", ldap_dn="dc=company,dc=com"
        ),
        ldap_manager_settings=OverhaveLdapManagerSettings(ldap_admin_group="admin"),
        stash_project_settings=OverhaveStashPublisherSettings(
            repository_name='bdd-features',
            key='PRJ',
            default_target_branch_name='master',
            default_reviewers=["admin"],
        ),
        stash_client_settings=OverhaveStashClientSettings(url="https://stash.company.com", auth_token="secret_token"),
    )
