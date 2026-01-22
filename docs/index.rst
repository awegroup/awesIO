.. awesIO documentation master file

======
awesIO
======

**YAML schemas for Airborne Wind Energy systems**

awesIO is a standardized input/output specification for Airborne Wind Energy (AWE) 
systems, providing YAML schemas that define data formats for kites, tethers, ground 
stations, wind resources, and complete AWE system configurations.

.. note::
   awesIO is inspired by and follows the architecture of 
   `windIO <https://github.com/IEAWindTask37/windIO>`_, the IEA Wind Task 37 
   ontology for traditional wind turbines.

What is awesIO?
===============

awesIO provides a common language for describing AWE systems, enabling:

* **Interoperability** between different AWE simulation tools and frameworks
* **Standardized data exchange** for research collaboration
* **Validation** of input files against formal schemas
* **Documentation** of AWE system specifications

Key Features
------------

* YAML-based schemas - Human-readable, version-controllable specifications
* Built-in validation - Automatic checking of input file correctness
* Tool integration - Works with simulation frameworks like AWESPA
* Comprehensive coverage - Schemas for all major AWE subsystems

AWE System Components
=====================

awesIO defines schemas for complete AWE systems and their operational parameters:

.. list-table::
   :header-rows: 1
   :widths: 20 50 30

   * - Component
     - Description
     - Schema Reference
   * - **Complete System**
     - Wing, bridle, control system, tether, and ground station in one schema
     - :doc:`source/system_schema`
   * - **Wind Resource**
     - Wind profile clusters, probability distributions
     - :doc:`source/wind_resource_schema`
   * - **Power Curves**
     - Power output vs. wind speed relationships
     - :doc:`source/power_curves_schema`
   * - **Operational Constraints**
     - Operating limits, safety boundaries, terrain constraints
     - :doc:`source/operational_constraints_schema`


Getting Started
===============

Installation
------------

Install using pip
~~~~~~~~~~~~~~~~~

Install the latest version from the main branch:

.. code-block:: bash

   pip install git+https://github.com/awegroup/awesIO.git

Install from a specific branch, commit, or tag:

.. code-block:: bash

   pip install git+https://github.com/awegroup/awesIO.git@branch-name
   pip install git+https://github.com/awegroup/awesIO.git@commit-hash
   pip install git+https://github.com/awegroup/awesIO.git@v0.1.0

Install using pixi
~~~~~~~~~~~~~~~~~~

Install the latest version:

.. code-block:: bash

   pixi add --pypi "awesio @ git+https://github.com/awegroup/awesIO.git"

Install from a specific branch, commit, or tag:

.. code-block:: bash

   pixi add --pypi "awesio @ git+https://github.com/awegroup/awesIO.git@branch-name"
   pixi add --pypi "awesio @ git+https://github.com/awegroup/awesIO.git@commit-hash"
   pixi add --pypi "awesio @ git+https://github.com/awegroup/awesIO.git@v0.1.0"

For developers
~~~~~~~~~~~~~~

Clone and install in development mode:

.. code-block:: bash

   git clone https://github.com/awegroup/awesIO.git
   cd awesIO
   pip install -e .
   pip install -r docs/requirements.txt

Or use pixi:

.. code-block:: bash

   git clone https://github.com/awegroup/awesIO.git
   cd awesIO
   pixi run validate

Quick Example
-------------

Here's a simple example of validating an AWE configuration:

.. code-block:: python

   from awesio.validator import validate
   
   # Auto-detects schema from file metadata
   validated_data = validate("path/to/config.yml")
   
   # Access validated data
   print(f"System name: {validated_data['metadata']['name']}")

Validation Script
-----------------

Validate multiple files at once:

.. code-block:: bash

   # Edit scripts/validate_yaml.py to set file paths
   python scripts/validate_yaml.py

Schema Auto-Detection
---------------------

Each YAML file must include a schema reference in its metadata:

.. code-block:: yaml

   metadata:
     name: My AWE System
     description: System description
     note: Additional notes
     awesIO_version: 0.1.0
     schema: system_schema.yml  # Auto-detected by validator

Table of Contents
=================

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   source/getting_started

.. toctree::
   :maxdepth: 3
   :caption: Schema Reference

   source/system_schema
   source/wind_resource_schema
   source/power_curves_schema
   source/operational_constraints_schema

.. toctree::
   :maxdepth: 2
   :caption: Development

   source/developer_guide
   source/changelog


Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


Contributing
============

awesIO is developed by the AWE research community. Contributions are welcome!

* **GitHub**: https://github.com/awegroup/awesIO
* **Issues**: https://github.com/awegroup/awesIO/issues

License
=======

awesIO is released under the MIT License. See the LICENSE file for details.
