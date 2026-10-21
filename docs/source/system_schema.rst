AWE System Schema
==================================

The system configuration schema defines the physical properties of a complete AWE
system in a **single file**. All system components — wing, bridle, control system,
tether, and ground station — are described together at the same hierarchy level. This
flat, modular structure reflects the physical organization of an AWE system and makes
it straightforward to identify, version, and exchange complete system definitions.

Aerodynamic properties are intentionally excluded from the system configuration.
Aerodynamic models are tool-dependent: some tools work with a small number of
coefficients for a limited set of operating states, while others use higher-fidelity
models to determine the full aerodynamic behaviour of the kite or aircraft. Keeping
aerodynamics outside the system schema avoids imposing one model structure on all
tools.

Validation, units, versioning and a tool's own blocks follow the :doc:`conventions`
every awesIO file shares.

Component Types
---------------

AWE systems vary in physical layout and operating principle. A fly-generation system
may use a conductive tether, while a ground-generation system uses a non-conductive
tether. The airborne component can be a leading-edge inflatable soft kite, a ram-air
kite, a single-skin kite, or a fixed-wing aircraft.

To represent this variety within a single schema, each component specifies a
**component type**. The type determines which fields are required or applicable for
that component, for example:

* A **conductive tether** requires different parameters than a **non-conductive
  tether**.
* A **soft kite** (ram-air, single-skin, or leading-edge inflatable) requires
  different properties than a **fixed-wing aircraft**.

Where possible, parameters are kept consistent across related component types to
support comparison between designs and reduce unnecessary differences between similar
systems.

Each component also includes a **name** and **version** identifier. These metadata
fields improve traceability by making clear which component definition is used.
Equivalent metadata are also included at the top level of the file, so that the full
system configuration can be identified and versioned consistently.

Schema File
-----------

.. code-block:: text

   src/awesio/schemas/system_schema.yml

Example File
------------

See: ``examples/ground_gen/soft_kite_pumping_ground_gen_system.yml``

Schema Structure
----------------

.. jsonschema:: ../../src/awesio/schemas/system_schema.yml
   :auto_reference:
