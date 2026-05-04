.. awesIO documentation master file

===============
What is awesIO?
===============

awesIO (Airborne Wind Energy Systems Input/Output) is a standardized and validated
data framework for airborne wind energy (AWE) applications. Its purpose is to provide
a tool-independent format for system configurations, environmental conditions, and
simulation inputs and outputs.

The framework uses human-readable YAML files that follow predefined schemas. These
schemas define the structure, naming conventions, and required fields for each file
type. This enables different tools to interpret the same files in a consistent and
unambiguous way. By using a common data format, awesIO allows independently developed
models to exchange data without tool-specific manual conversion.

.. note::
   All quantities in awesIO are expressed in **SI units** throughout all schemas
   and example files.

.. note::
   awesIO is inspired by and follows the architecture of
   `windIO <https://github.com/IEAWindTask37/windIO>`_, the IEA Wind Task 37
   ontology for traditional wind turbines.

Goals
=====

The key goals of the awesIO framework are:

* **Interoperability** — different AWE simulation tools can read and write the same
  files without custom adapters or manual conversion.
* **Standardization** — a shared naming convention and file structure reduces
  ambiguity in data exchange between research groups and tools.
* **Validation** — files can be checked for compliance with the schema before or
  after a simulation run, reducing errors caused by incomplete or inconsistent inputs.
* **Collaboration** — a public, common format makes it easier to compare results
  from different models, evaluate alternative system designs, and reproduce results.

Validation
==========

A central feature of awesIO is its built-in validation capability. Before a file is
used in a simulation, or after it has been produced, it can be verified for:

* compliance with the defined schema,
* presence of all required parameters,
* consistent naming conventions.

This validation step makes it explicit whether a file conforms to the awesIO standard,
helping to prevent errors from reaching the simulation stage.

Schemas
=======

awesIO currently contains four schemas, covering the main data exchanged in a
performance assessment workflow:

* :doc:`source/system_schema` — the central schema describing the complete AWE
  system, including wing, bridle, control system, tether, and ground station.
* :doc:`source/wind_resource_schema` — site-specific wind conditions.
* :doc:`source/power_curves_schema` — power output as a function of wind speed.
* :doc:`source/operational_constraints_schema` — limits that restrict system
  operation.

Standardizing these files allows the main inputs and outputs of a performance
assessment to be exchanged between tools in a consistent way. For example, different
power estimation models can be evaluated using the same wind resource and system
description, enabling direct comparison of modelling approaches.

Availability
============

awesIO is hosted on `GitHub <https://github.com/awegroup/awesIO>`_, making the
schemas, documentation, and examples freely accessible to researchers and developers.
It can also be developed collaboratively through issues, discussions, and contributions
to the repository. The validation functionality is available as a Python package
installable via ``pip``, so researchers can check their own files directly from their
workflow.

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   self
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

* **GitHub**: https://github.com/awegroup/awesIO
* **Issues**: https://github.com/awegroup/awesIO/issues

License
=======

awesIO is released under the MIT License. See the LICENSE file for details.
