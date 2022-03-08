========
Overhave
========

.. figure:: https://raw.githubusercontent.com/TinkoffCreditSystems/overhave/master/docs/includes/images/label_img.png
  :width: 700
  :align: center
  :alt: Overhave framework

  `Overhave`_ is the web-framework for BDD: scalable, configurable, easy to use, based on
  `Flask Admin`_ and `Pydantic`_.

  .. image:: https://github.com/TinkoffCreditSystems/overhave/workflows/CI/badge.svg
    :target: https://github.com/TinkoffCreditSystems/overhave/actions?query=workflow%3ACI
    :alt: CI

  .. image:: https://img.shields.io/pypi/pyversions/overhave.svg
    :target: https://pypi.org/project/overhave
    :alt: Python versions

  .. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/TinkoffCreditSystems/overhave
    :alt: Code style

  .. image:: https://img.shields.io/pypi/v/overhave?color=%2334D058&label=pypi%20package
    :target: https://pypi.org/project/overhave
    :alt: Package version
    
  .. image:: https://img.shields.io/pypi/dm/overhave.svg
    :target: https://pypi.org/project/overhave
    :alt: Downloads per month

--------
Features
--------

* Ready web-interface for easy BDD features management with `Ace`_ editor
* Traditional Gherkin format for scenarios provided by `pytest-bdd`_
* Execution and reporting of BDD features based on `PyTest`_  and `Allure`_
* Auto-collection of `pytest-bdd`_ steps and display on the web-interface
* Simple business-alike scenarios structure, easy horizontal scaling
* Built-in wrappers for `pytest-bdd`_ hooks to supplement `Allure`_ report
* Ability to create and use several BDD keywords dictionary with different languages
* Versioning and deployment of scenario drafts to `Bitbucket`_ or `GitLab`_
* Synchronization between `git`_ repository and database with features
* Built-in configurable management of users and groups permissions
* Configurable strategy for user authorization, LDAP also provided
* Database schema based on `SQLAlchemy`_ models and works with PostgreSQL
* Still configurable as `Flask Admin`_, supports plug-ins and extensions
* Distributed `producer-consumer` architecture based on Redis streams
  through `Walrus`_
* Web-browser emulation ability with custom toolkit (`GoTTY`_, for example)
* Simple command-line interface, provided with `Typer`_
* Integrated interaction for files storage with s3-cloud based on `boto3`_

------------
Installation
------------

You can install **Overhave** via pip from PyPI:

.. code-block:: shell

    pip install overhave

--------
Overview
--------

Web-interface
-------------

The web-interface is a basic tool for BDD features management. It consists of:

* `Info` - index page with optional information about your tool or project;
* `Scenarios` - section for features management, contains subsections
    `Features`, `Test runs` and `Versions`:

    * `Features`
        gives an interface for features records management and provides info
        about id, name author, time, editor and publishing status; it is possible
        to search, edit or delete items through Script panel.

        .. figure:: https://raw.githubusercontent.com/TinkoffCreditSystems/overhave/master/docs/includes/images/label_img.png
          :width: 500
          :align: center
          :alt: Features list

    * `Test runs`
        gives an interface for test runs management and provides info about.

        .. figure:: https://raw.githubusercontent.com/TinkoffCreditSystems/overhave/master/docs/includes/images/test_runs_img.png
          :width: 500
          :align: center
          :alt: Test runs list

    * Versions
        contains feature versions in corresponding to test runs; versions contains PR-links to
        the remote Git repository (only Stash is supported now).

        .. figure:: https://raw.githubusercontent.com/TinkoffCreditSystems/overhave/master/docs/includes/images/versions_img.png
          :width: 500
          :align: center
          :alt: Feature published versions list

    * Tags
        contains tags values, which are used for feature's tagging.

        .. figure:: https://raw.githubusercontent.com/TinkoffCreditSystems/overhave/master/docs/includes/images/tags_img.png
          :width: 500
          :align: center
          :alt: Feature published versions list

* `Access` - section for access management, contains `Users` and
    `Groups` subsections;
* `Emulation` - experimental section for alternative tools implementation
    (in development).

**Overhave** features could be created and/or edited through special
*script panel* in feature edit mode. Feature should have type registered by the
application, unique name, specified tasks list with the traditional format
```PRJ-NUMBER``` and scenario text.

**Script panel** has `pytest-bdd`_ steps table on the right side of interface.
These steps should be defined in appropriate fixture modules and registered
at the application on start-up to be displayed.


.. figure:: https://raw.githubusercontent.com/TinkoffCreditSystems/overhave/master/docs/includes/images/panel_img.png
  :width: 600
  :align: center
  :alt: Script panel

  Example of **Overhave** script panel in feature edit mode

Allure report
-------------

**Overhave** generates `Allure`_ report after tests execution in web-interface.
If you execute tests manually through `PyTest`_, these results are could be
converted into the `Allure`_ report also with the `Allure CLI`_ tool.
This report contains scenarios descriptions as they are described in features.

.. figure:: https://raw.githubusercontent.com/TinkoffCreditSystems/overhave/master/docs/includes/images/report_img.png
  :width: 600
  :align: center
  :alt: Allure test-case report

  Example of generated `Allure`_ report after execution of **Overhave**'s feature

Demo-mode (Quickstart)
----------------------

**Overhave** has special demo-mode (in development), which could be possibly
used for framework demonstration and manual debugging / testing. The framework
provides a CLI entrypoints for easy server run in debug mode:

.. code-block:: shell

    make up  # start PostgreSQL database and Redis
    overhave db create-all  # create Overhave database schema
    overhave-demo admin  # start Overhave admin on port 8076 in debug mode
    overhave-demo consumer -s test  # start Overhave test execution consumer

**Note**: you could run admin in special mode, which does not require
consumers. This mode uses *threadpool* for running testing and publication
tasks asynchronously:

.. code-block:: shell

    overhave-demo admin --threadpool --language=ru

But this *threadpool* mode is unscalable in *kubernetes* paradigm. So,
it's highly recommended to use corresponding consumers exactly.

Command-line interface
----------------------

**Overhave** has a CLI that provides a simple way to start service web-interface,
run consumer and execute basic database operations. Examples are below:

.. code-block:: shell

    overhave db create-all
    overhave admin --port 8080
    overhave consumer -s publication

**Note**: service start-up takes a set of settings, so you can set them through
virtual environment with prefix ```OVERHAVE_```, for example ```OVERHAVE_DB_URL```.
If you want to configure settings in more explicit way through context injection,
please see next part of docs.

Context injection
-----------------

Context setting
^^^^^^^^^^^^^^^

Service could be configured via application context injection with prepared
instance of `OverhaveContext` object. This context could be set using
```set_context``` function of initialized ```ProxyFactory``` instance.

For example, ```my_custom_context``` prepared. So, application start-up could
be realised with follow code:

.. code-block:: python

    from overhave import overhave_app, overhave_admin_factory

    factory = overhave_admin_factory()
    factory.set_context(my_custom_context)
    overhave_app(factory).run(host='localhost', port=8080, debug=True)

**Note**:

* ```overhave_app``` is the prepared `Flask` application with already enabled
    Flask Admin and Login Manager plug-ins;
* ```overhave_factory``` is a function for LRU cached instance of the **Overhave**
    factory ```ProxyFactory```; the instance has an access to application components,
    directly used in ```overhave_app```.
* ```my_custom_context``` is an example of context configuration, see an
    example code in `context_example.rst`_.

Enabling of injection
^^^^^^^^^^^^^^^^^^^^^

**Overhave** has it's own built-in `PyTest`_ plugin, which is used to enable
and configure injection of prepared context into application core instance.
The plugin provides one option:

* `--enable-injection` - flag to enable context injection.

The `PyTest` usage should be similar to:

.. code-block:: bash

    pytest --enable-injection


Consumers
---------

**Overhave** has `producer-consumer` architecture, based on Redis streams,
and supported 3 consumer's types:

* **TEST** - consumer for test execution with it's own factory
    ```overhave_test_execution_factory```;

* **PUBLICATION** - consumer for features publication with it's own factory
    ```overhave_publication_factory```;

* **EMULATION** - consumer for specific emulation with it's own factory
    ```overhave_emulation_factory```.

**Note**: the ```overhave_test_execution_factory``` has ability for context injection
and could be enriched with the custom context as the ```overhave_admin_factory```.


Project structure
-----------------

**Overhave** supports it's own special project structure:

.. image:: https://raw.githubusercontent.com/TinkoffCreditSystems/overhave/master/docs/includes/images/project_structure.png
  :width: 300
  :alt: **Overhave** project structure

The right approach is to create a **root directory** (like "demo" inside the current
repository) that contains **features**, **fixtures** and **steps** directories.

The **Features** directory contains different feature types as
separate directories, each of them corresponds to predefined `pytest-bdd`_
set of steps.

The **Fixtures** directory contains typical `PyTest`_ modules splitted by different
feature types. These modules are used for `pytest-bdd`_ isolated test runs. It is
necessary because of special mechanism of `pytest-bdd`_ steps collection.

The **Steps** directory contains `pytest-bdd`_ steps packages splitted by differrent
feature types also. Each steps subdirectory has it's own declared steps in according
to supported feature type.

So, it is possible to create your own horizontal structure of
different product directions with unique steps and `PyTest`_ fixtures.

**Note**: this structure is used in **Overhave** application. The formed data
gives a possibility to specify registered feature type in the web-interface
*script panel*. Also, this structure defines which steps will be displayed in
the right side of *script panel*.

Feature format
--------------

**Overhave** has it's own special feature's text format, which inherits
Gherkin from `pytest-bdd`_ with small updates:

* required tag that is related to existing feature type directory, where
    current feature is located;
* info about feature - who is creator, last editor and publisher;
* task tracker's tickets with traditional format ```PRJ-NUMBER```.

An example of filled feature content is located in
`feature_example.rst`_.

Language
--------

The web-interface language is ENG by default and could not be switched
(if it's necessary - please, create a ```feature request``` or contribute
yourself).

The feature text as well as `pytest-bdd`_ BDD keywords are configurable
with **Overhave** extra models, for example RUS keywords are already defined
in framework and available for usage:

.. code-block:: python

    from overhave.extra import RUSSIAN_PREFIXES

    language_settings = OverhaveLanguageSettings(step_prefixes=RUSSIAN_PREFIXES)

**Note**: you could create your own prefix-value mapping for your language:

.. code-block:: python

    from overhave import StepPrefixesModel

    GERMAN_PREFIXES = StepPrefixesModel(
        FEATURE="Merkmal:",
        SCENARIO_OUTLINE="Szenarioübersicht:",
        SCENARIO="Szenario:",
        BACKGROUND="Hintergrund:",
        EXAMPLES="Beispiele:",
        EXAMPLES_VERTICAL="Beispiele: Vertikal",
        GIVEN="Gegeben ",
        WHEN="Wann ",
        THEN="Dann ",
        AND="Und ",
        BUT="Aber ",
    )


Git integration
---------------

**Overhave** gives an ability to sent your new features or changes to
remote git repository, which is hosted by `Bitbucket`_ or `GitLab`_.
Integration with bitbucket is native, while integration with GitLab
uses `python-gitlab`_ library.

You are able to set necessary settings for your project:

.. code-block:: python

    publisher_settings = OverhaveGitlabPublisherSettings(
        repository_id='123',
        default_target_branch_name='master',
    )
    client_settings=OverhaveGitlabClientSettings(
        url="https://gitlab.mycompany.com",
        auth_token=os.environ.get("MY_GITLAB_AUTH_TOKEN"),
    )

The pull-request (for Bitbucket) or merge-request (for GitLab)
created when you click the button `Create pull request` on
test run result's page. This button is available only for `success`
test run's result.

**Note**: one of the most popular cases of GitLab API
authentication is the OAUTH2 schema with service account.
In according to this schema, you should have OAUTH2 token,
which is might have a short life-time and could not be
specified through environment. For this situation, **Overhave**
has special `TokenizerClient` with it's own
`TokenizerClientSettings` - this simple client could take
the token from a remote custom GitLab tokenizer service.


Git-to-DataBase synchronization
-------------------------------

**Overhave** gives an ability to synchronize your current `git`_
repository's state with database. It means that your features,
which are located on the database, could be updated - and the source
of updates is your repository.

**For example**: you had to do bulk data replacement in `git`_
repository, and now you want to deliver changes to remote database.
This not so easy matter could be solved with **Overhave** special
tooling:

You are able to set necessary settings for your project:

.. code-block:: bash

    overhave synchronize  # only update existing features
    overhave synchronize --create-db-features  # update + create new features

You are able to test this tool with **Overhave** demo mode.
By default, 3 features are created in demo database. Just try
to change them or create new features and run synchronization
command - you will get the result.

.. code-block:: bash

    overhave-demo synchronize  # or with '--create-db-features'


Custom index
------------

**Overhave** gives an ability to set custom index.html file for rendering. Path
to file could be set through environment as well as set with context:

.. code-block:: python

    admin_settings = OverhaveAdminSettings(
        index_template_path="/path/to/index.html"
    )


Authorization strategy
----------------------

**Overhave** provides several authorization strategies, declared by
```AuthorizationStrategy``` enum:

* `Simple` - strategy without real authorization.
    Each user could use preferred name. This name will be used for user
    authority. Each user is unique. Password not required.

* `Default` - strategy with real authorization.
    Each user could use only registered credentials.

* `LDAP` - strategy with authorization using remote LDAP server.
    Each user should use his LDAP credentials. LDAP
    server returns user groups. If user in default 'admin' group or his groups
    list contains admin group - user will be authorized. If user already placed
    in database - user will be authorized too. No one password stores.

Appropriate strategy and additional data should be placed into
```OverhaveAuthorizationSettings```, for example LDAP strategy could be
configured like this:

.. code-block:: python

    auth_settings=OverhaveAuthorizationSettings(
        auth_strategy=AuthorizationStrategy.LDAP, admin_group="admin"
    )

S3 cloud
--------

**Overhave** implements functionality for *s3* cloud interactions, such as
bucket creation and deletion, files uploading, downloading and deletion.
The framework provides an ability to store reports and other files in
the remote s3 cloud storage. You could enrich your environment with following
settings:

.. code-block:: shell

    OVERHAVE_S3_ENABLED=true
    OVERHAVE_S3_URL=https://s3.example.com
    OVERHAVE_S3_ACCESS_KEY=<MY_ACCESS_KEY>
    OVERHAVE_S3_SECRET_KEY=<MY_SECRET_KEY>

Optionally, you could change default settings also:

.. code-block:: shell

    OVERHAVE_S3_VERIFY=false
    OVERHAVE_S3_AUTOCREATE_BUCKETS=true

The framework with enabled ```OVERHAVE_S3_AUTOCREATE_BUCKETS``` flag will create
application buckets in remote storage if buckets don't exist.

------------
Contributing
------------

Contributions are very welcome.

Preparation
-----------

Project installation is very easy
and takes just few prepared commands (`make pre-init` works only for Ubuntu;
so you can install same packages for your OS manually):

.. code-block:: shell

    make pre-init
    make init

Packages management is provided by `Poetry`_.

Check
-----

Tests can be run with `Tox`_. `Docker-compose`_ is used for other services
preparation and serving, such as database. Simple tests and linters execution:

.. code-block:: shell

    make up
    make test
    make lint

Please, see `make` file and discover useful shortcuts. You could run tests
in docker container also:

.. code-block:: shell

    make test-docker

Documentation build
-------------------

Project documentation could be built via `Sphinx`_ and simple `make` command:

.. code-block:: shell

    make build-docs

By default, the documentation will be built using `html` builder into `_build`
directory.

-------
License
-------

Distributed under the terms of the `GNU GPLv2`_ license.

------
Issues
------

If you encounter any problems, please report them here in section `Issues`
with a detailed description.

.. _`Overhave`: https://github.com/TinkoffCreditSystems/overhave
.. _`Pydantic`: https://github.com/samuelcolvin/pydantic
.. _`Flask Admin`: https://github.com/flask-admin/flask-admin
.. _`Ace`: https://github.com/ajaxorg/ace
.. _`PyTest`: https://github.com/pytest-dev/pytest
.. _`pytest-bdd`: https://github.com/pytest-dev/pytest-bdd
.. _`Allure`: https://github.com/allure-framework/allure-python
.. _`Allure CLI`: https://docs.qameta.io/allure/#_get_started
.. _`Bitbucket`: https://www.atlassian.com/git
.. _`GitLab`: https://about.gitlab.com
.. _`python-gitlab`: https://python-gitlab.readthedocs.io
.. _`SQLAlchemy`: https://github.com/sqlalchemy/sqlalchemy
.. _`Walrus`: https://github.com/coleifer/walrus
.. _`GoTTY`: https://github.com/yudai/gotty
.. _`GNU GPLv2`: http://www.apache.org/licenses/LICENSE-2.0
.. _`Tox`: https://github.com/tox-dev/tox
.. _`Poetry`: https://github.com/python-poetry/poetry
.. _`Docker-compose`: https://docs.docker.com/compose
.. _`Typer`: https://github.com/tiangolo/typer
.. _`Sphinx`: https://github.com/sphinx-doc/sphinx
.. _`boto3`: https://github.com/boto/boto3
.. _`git`: https://git-scm.com/
.. _`context_example.rst`: https://github.com/TinkoffCreditSystems/overhave/blob/master/docs/includes/context_example.rst
.. _`feature_example.rst`: https://github.com/TinkoffCreditSystems/overhave/blob/master/docs/includes/features_structure_example/feature_type_1/full_feature_example_en.feature
