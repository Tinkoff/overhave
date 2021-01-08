========
Overhave
========

Overhave is a web-framework for BDD: scalable, configurable, easy to use,
based on `Pydantic`_ and `Flask Admin`_.

--------
Features
--------

* Ready web-interface for easy BDD scenarios management
* Traditional Gherkin format for scenarios provided by `pytest-bdd`_
* Execution and reporting of BDD scenarios based on `PyTest`_  and `Allure`_
* Auto-collection of `pytest-bdd`_ steps and display on the web-interface
* Simple business-alike scenarios structure, easy horizontal scaling
* Versioning and deployment of scenario drafts to `Bitbucket`_
* Built-in configurable management of users and groups permissions
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

-----------
Quick start
-----------

Command-line interface
----------------------
**Overhave** has a CLI that provides a simple way to start service web-interface,
run consumer and execute basic database operations. Examples are below:

.. code-block:: shell

    overhave admin --port 8080
    overhave db create-all
    overhave consumer -s EMULATION

**Note**: service start-up takes a set of settings, so you can set them through
virtual environment with prefix ```OVERHAVE_```, for example ```OVERHAVE_DB_URL```. If
you want to configure settings in more explicit way through context injection,
please see next part of docs.

Context injection
-----------------

Service could be configured via application context injection with prepared
instance of `OverhaveContext` object. This context should be set using
``overhave_core.set_context`` function.

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

And an example of context configuration for ```my_custom_context``` placed below:

.. include:: docs/context_example.rst

Features structure
------------------

**Overhave** supports it's own special structure of features storage:

.. figure:: docs/features_structure_img.png
  :width: 400
  :alt: Features structure example

**Base features directory** could contain different feature types as
separate directories, each of them corresponds to predefined `pytest-bdd`_
set of steps. It is possible to create your own horizontal structure of
different product directions with unique steps and `PyTest`_ fixtures.

------------
Contributing
------------
Contributions are very welcome. Project installation is very easy
and takes just few prepared commands (`make pre-init` works only for Ubuntu;
so you can install same packages for your OS manually):

.. code-block:: shell

    make pre-init
    make init

Packages management is provided by `Poetry`_. Tests can be run with `Tox`_.
`Docker-compose`_ is used for other services preparation and serving, such as
database. Simple tests and linters execution:

.. code-block:: shell

    docker-compose up -d db
    make test
    make lint

Please, see `make` file and discover useful shortcuts. You could run tests
in docker container also:

.. code-block:: shell

    make test-docker

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