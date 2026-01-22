===============
Getting Started
===============

awesIO provides YAML schemas and validation utilities for airborne wind energy
system configurations. This page covers installation, basic validation, and how
to choose the right schema for your data.

Prerequisites
=============

- Python 3.9 or newer
- A YAML file that includes a schema reference in ``metadata.schema``

Install
=======

Install using pip
-----------------

Install the latest version from the main branch:

.. code-block:: bash

   pip install git+https://github.com/awegroup/awesIO.git

Install from a specific branch:

.. code-block:: bash

   pip install git+https://github.com/awegroup/awesIO.git@branch-name

Install from a specific commit or tag:

.. code-block:: bash

   pip install git+https://github.com/awegroup/awesIO.git@commit-hash
   pip install git+https://github.com/awegroup/awesIO.git@v0.1.0

Install using pixi
------------------

Install the latest version:

.. code-block:: bash

   pixi add --pypi "awesio @ git+https://github.com/awegroup/awesIO.git"

Install from a specific branch:

.. code-block:: bash

   pixi add --pypi "awesio @ git+https://github.com/awegroup/awesIO.git@branch-name"

Install from a specific commit or tag:

.. code-block:: bash

   pixi add --pypi "awesio @ git+https://github.com/awegroup/awesIO.git@commit-hash"
   pixi add --pypi "awesio @ git+https://github.com/awegroup/awesIO.git@v0.1.0"

Validate a YAML file
====================

The validator auto-detects the schema using ``metadata.schema``.

.. code-block:: python

   from awesio.validator import validate

   data = validate("path/to/your_file.yml")

If validation fails, the error message includes the exact path of the
failing property and the expected constraints.

Schema selection
================

Choose the schema by setting the schema filename in the YAML metadata.

.. code-block:: yaml

   metadata:
     name: Example configuration
     description: System description
     note: Notes for reviewers
     awesIO_version: 0.1.0
     schema: system_schema.yml

Available schemas
=================

- ``system_schema.yml``: complete airborne system configurations
- ``power_curves_schema.yml``: power curve datasets
- ``wind_resource_schema.yml``: wind resource data
- ``operational_constraints_schema.yml``: operational constraints

Examples
========

File examples are available in the ``examples/`` directory. Start with:

- ``examples/ground_gen/soft_kite_pumping_ground_gen_system.yml``
- ``examples/ground_gen/soft_kite_pumping_ground_gen_power_curves.yml``
- ``examples/ground_gen/soft_kite_pumping_ground_gen_operational_constraints.yml``
- ``examples/wind_resource.yml``

Next steps
==========

- Review the schema reference pages for field definitions.
- Use the developer guide if you plan to contribute.

