========
Overhave
========

.. figure:: https://raw.githubusercontent.com/TinkoffCreditSystems/overhave/master/docs/includes/images/label_img.png
  :width: 600
  :align: center
  :alt: Overhave framework

  Web-framework for BDD: scalable, configurable, easy to use, based on `Flask Admin`_ and `Pydantic`_.

  .. image:: https://github.com/TinkoffCreditSystems/overhave/workflows/CI/badge.svg
    :target: https://github.com/TinkoffCreditSystems/overhave/actions?query=workflow%3ACI
    :alt: CI

  .. image:: https://img.shields.io/pypi/pyversions/overhave.svg
    :target: https://pypi.org/project/overhave
    :alt: Python versions

  .. image:: https://img.shields.io/pypi/v/overhave?color=%2334D058&label=pypi%20package
    :target: https://pypi.org/project/overhave
    :alt: Package version

--------
Features
--------

* Ready web-interface for easy BDD features management with `Ace`_ editor
* Traditional Gherkin format for scenarios provided by `pytest-bdd`_
* Execution and reporting of BDD features based on `PyTest`_  and `Allure`_
* Auto-collection of `pytest-bdd`_ steps and display on the web-interface
* Simple business-alike scenarios structure, easy horizontal scaling
* Ability to create and use several BDD keywords dictionary with different languages
* Versioning and deployment of scenario drafts to `Bitbucket`_
* Built-in configurable management of users and groups permissions
* Configurable strategy for user authorization, LDAP also provided
* Database schema based on `SQLAlchemy`_ models and works with PostgreSQL
* Still configurable as `Flask Admin`_, supports plug-ins and extensions
* Distributed `producer-consumer` architecture based on Redis streams
  through `Walrus`_ (partially integrated)
* Web-browser emulation ability with custom toolkit (`GoTTY`_, for example)
* Simple command-line interface, provided with `Click`_

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
        to search, edit or delete items through interface;
    * `Test runs`
        gives an interface for test runs management and provides info about

        .. figure:: https://raw.githubusercontent.com/TinkoffCreditSystems/overhave/master/docs/includes/images/test_runs_img.png
          :width: 500
          :align: center
          :alt: Script panel
    * Versions
        contains feature versions for corresponding to test runs.

* `Access` - section for access management, contains `Users` and
    `Groups` subsections;
* `Emulation` - experimental section for alternative tools implementation
    (in developing).

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

Command-line interface
----------------------
**Overhave** has a CLI that provides a simple way to start service web-interface,
run consumer and execute basic database operations. Examples are below:

.. code-block:: shell

    overhave db create-all
    overhave admin --port 8080
    overhave consumer -s EMULATION

**Note**: service start-up takes a set of settings, so you can set them through
virtual environment with prefix ```OVERHAVE_```, for example ```OVERHAVE_DB_URL```.
If you want to configure settings in more explicit way through context injection,
please see next part of docs.

Context injection
-----------------

Context setting
^^^^^^^^^^^^^^^

Service could be configured via application context injection with prepared
instance of `OverhaveContext` object. This context should be set using
```overhave_core.set_context``` function.

For example, ```my_custom_context``` prepared. So, application start-up could
be realised with follow code:

.. code-block:: python

    from overhave import overhave_app, overhave_core

    overhave_core.set_context(my_custom_context)
    overhave_app().run(host='localhost', port=8080, debug=True)

**Note**:

* ```overhave_app``` is the prepared `Flask` application with already enabled
    Flask Admin and Login Manager plug-ins;
* ```overhave_core``` is a cached instance of the **Overhave** factory, has an
    access to application components, directly used in ```overhave_app```.
* ```my_custom_context``` is an example of context configuration, see an
    example code in `context_example.rst`_.

Import context in PyTest
^^^^^^^^^^^^^^^^^^^^^^^^

**Overhave** has it's own built-in `PyTest`_ plugin, which is used to enable
and configure injection of prepared context into application core
```overhave_core```. The plugin provides two options:

* `--enable-injection` - flag to enable context injection;

* `--ctx-module` - option specifying path to Python module with context injection.

The module with context injection should contain
```overhave_core.set_context``` function, but this module should be
unique and created only for `PyTest`_ usage instead of web-interface start-up.

For example, ```module_with_injection.py``` module contains:

.. code-block:: python

    from overhave import overhave_core

    overhave_core.set_context(my_custom_context)

And `PyTest` usage should be similar to:

.. code-block:: bash

    pytest --enable-injection --ctx-module=module_with_injection

Specified module will be imported before tests start-up (with
```pytest_configure``` `PyTest`_ hook).


Features structure
------------------

**Overhave** supports it's own special structure of features storage:

.. image:: https://raw.githubusercontent.com/TinkoffCreditSystems/overhave/master/docs/includes/images/features_structure_img.png
  :width: 400
  :alt: Features structure example

**Base features directory** could contain different feature types as
separate directories, each of them corresponds to predefined `pytest-bdd`_
set of steps. It is possible to create your own horizontal structure of
different product directions with unique steps and `PyTest`_ fixtures.

**Note**: this structure is used in **Overhave** application. The formed data
gives a possibility to specify registered feature type in the web-interface
*script panel*. Also, this structure defines which steps will be displayed in
the rigth side of *script panel*.

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

    from overhave.extra import RUSSIAN_PREFIXES, RUSSIAN_TRANSLIT_PACK

    language_settings = OverhaveLanguageSettings(
        step_prefixes=RUSSIAN_PREFIXES,
        translit_pack=RUSSIAN_TRANSLIT_PACK
    )

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
    Every user could use preferred name. This name will be used for user
    authority. Every user is unique. Password not required.

* `Default` - strategy with real authorization.
    Every user could use only registered credentials.

* LDAP - strategy with authorization using remote LDAP server.
    Every user should use his LDAP credentials. LDAP
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

    docker-compose up -d db
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

.. _`Pydantic`: https://github.com/samuelcolvin/pydantic
.. _`Flask Admin`: https://github.com/flask-admin/flask-admin
.. _`Ace`: https://github.com/ajaxorg/ace
.. _`PyTest`: https://github.com/pytest-dev/pytest
.. _`pytest-bdd`: https://github.com/pytest-dev/pytest-bdd
.. _`Allure`: https://github.com/allure-framework/allure-python
.. _`Bitbucket`: https://www.atlassian.com/git
.. _`SQLAlchemy`: https://github.com/sqlalchemy/sqlalchemy
.. _`Walrus`: https://github.com/coleifer/walrus
.. _`GoTTY`: https://github.com/yudai/gotty
.. _`GNU GPLv2`: http://www.apache.org/licenses/LICENSE-2.0
.. _`Tox`: https://github.com/tox-dev/tox
.. _`Poetry`: https://github.com/python-poetry/poetry
.. _`Docker-compose`: https://docs.docker.com/compose
.. _`Click`: https://github.com/pallets/click
.. _`Sphinx`: https://github.com/sphinx-doc/sphinx
.. _`context_example.rst`: https://github.com/TinkoffCreditSystems/overhave/blob/master/docs/includes/context_example.rst
.. _`feature_example.rst`: https://github.com/TinkoffCreditSystems/overhave/blob/master/docs/includes/features_structure_example/feature_type_1/full_feature_example_en.feature