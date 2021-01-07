.. code-block:: python

    from overhave import (
        AuthorizationStrategy,
        LdapClientSettings,
        OverhaveAdminSettings,
        OverhaveAuthorizationSettings,
        OverhaveContext,
        OverhaveFileSettings,
        OverhaveLanguageSettings,
        OverhaveProjectSettings,
        StashClientSettings,
        StashProjectSettings,
    )
    from overhave.extra import RUSSIAN_PREFIXES, RUSSIAN_TRANSLIT_PACK

    my_custom_context = OverhaveContext(
        file_settings=OverhaveFileSettings(
            features_base_dir=path_settings.features_base_dir, tmp_dir=path_settings.tmp_dir
        ),
        language_settings=OverhaveLanguageSettings(
            step_prefixes=RUSSIAN_PREFIXES, translit_pack=RUSSIAN_TRANSLIT_PACK,
        ),
        project_settings=OverhaveProjectSettings(
            browse_url="https://jira.company.com/browse",
            links_keyword="Tasks",
        ),
        admin_settings=OverhaveAdminSettings(index_template_path=path_settings.index_template_path),
        auth_settings=OverhaveAuthorizationSettings(auth_strategy=AuthorizationStrategy.LDAP, admin_group="admin"),
        ldap_client_settings=LdapClientSettings(
            ldap_url="ldap://company.com", ldap_domain="company\\", ldap_dn="dc=company,dc=com"
        ),
        stash_project_settings=StashProjectSettings(
            repository_name='bdd-features',
            key='PRJ',
            default_target_branch_name='master',
            default_reviewer="admin",
        ),
        stash_client_settings=StashClientSettings(url="https://stash.company.com", auth_token="secret_token"),
    )
