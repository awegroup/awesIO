=========
Changelog
=========

This file documents notable changes to awesIO. Versions follow semantic
versioning.

Format
======

Each release includes the following sections when applicable:

- Added
- Changed
- Deprecated
- Removed
- Fixed
- Security

0.1.0 (draft)
=============

Added
-----

- Initial schema set for system, structure, power curves, wind resource, and
  operational constraints
- Validator with schema auto-detection from ``metadata.schema``
- Example YAML files for each schema, the two structure examples the TU Delft V3
  kite as V3Kite.jl's particle-lattice and Timoshenko-beam models build it
- Sphinx documentation with schema reference pages
- Conventions page for the rules every file shares, the ``_KA`` and ``_ENU``
  frames, ``Q_<from>2<to>`` rotations and bearings among them; the system, wind
  resource and operational constraints schemas accept extra top-level blocks a tool
  adds, as structure and power curves already did
- Terrain zones and wind directions are bearings in ``_ENU``; a wing's dihedral and
  sweep are measured in ``_KA``
- Angles in a YAML file are in degrees, the one exception to SI units:
  ``azimuth_range``, the wind direction bins, ``dihedral_angle``, ``sweep_angle`` and
  ``max_bank_angle``

Changed
-------

- Initial release, nothing changed

Fixed
-----

- Initial release, nothing fixed
