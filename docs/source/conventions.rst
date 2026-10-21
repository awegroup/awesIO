Conventions
===========

These rules hold for every awesIO file, whichever schema it follows. A schema page
states only what is specific to its own file.

Which schema a file follows
---------------------------

Every file opens with a ``metadata`` block. Its ``schema`` field is pinned to the
schema's filename, such as ``structure_schema.yml``, and names *which* schema the
file follows, never which version. ``awesio.validator.validate`` reads it to pick the schema, so a file is validated without being told its type:

.. code-block:: python

   from awesio.validator import validate

   data = validate("your_file.yml")

Units
-----

All quantities are in **SI units**, except angles in a YAML file, which are in
**degrees**. The time-history arrays in a companion ``.npz`` file are SI throughout,
angles in radians.

A table states the unit of each of its columns in a ``units`` row, one entry per
header, and spells each unit one way:

.. list-table::
   :header-rows: 1
   :widths: 1 4

   * - Unit
     - Quantity
   * - ``m``
     - length, position, diameter
   * - ``m^2``
     - area
   * - ``kg``
     - mass
   * - ``kg/m^2``
     - areal density
   * - ``kg/m^3``
     - density
   * - ``kg*m^2``
     - moment of inertia
   * - ``N``
     - force
   * - ``N/m``
     - force per length, such as a membrane stiffness
   * - ``Pa``
     - pressure
   * - ``deg``
     - angle
   * - ``-``
     - dimensionless, and a column holding names, flags, types, references or a law's
       parameters

A unit not listed is written the same way: SI symbols joined by ``*`` and ``/``,
powers with ``^``, such as ``m/s`` or ``N*m^2``. A schema pins the unit of every
column it requires, so a file writing ``mm`` where the schema says ``m`` does not
validate.

Versioning
----------

``metadata.awesIO_version`` is the version the file was written against. **A reader
refuses an unknown major version and warns on an unknown minor one**, so a breaking
change is caught at load rather than silently misread. A minor version only adds.

Names a reader does not know
----------------------------

A tool may carry data of its own as extra top-level blocks of any shape. ``metadata``
and the blocks a schema defines keep the keys that schema lists, except where the
schema opens one itself. **A reader ignores every name it does not know**, so a file
written for one tool still loads in another.

A later minor version may claim any such name for the schema, after which the tool
renames its own.

Frames
------

A vector's name ends in a suffix naming the frame it is written in. Every frame is
right-handed and in metres. The frames are those of `KiteUtils.jl
<https://opensourceawe.github.io/KiteUtils.jl/dev/reference_frames/>`_.

``_KA``
   A wing's or a body's own frame: x from the leading to the trailing edge, y from the
   right to the left tip, z up. Right and left are as seen looking at the kite from the
   front, so a turn to the right is a positive rotation about z. A wing's is the frame
   its aerodynamic mesh is drawn in, with its origin where the document puts it: the
   control unit of a soft kite.

``_ENU``
   The world: x east, y north, z up, with its origin at the tether exit point of the
   ground station.

A rotation reads ``Q_<from>2<to>``: a unit quaternion ``q``, scalar first
``[w, x, y, z]``, that takes a vector's components in ``<from>`` to the same vector's
components in ``<to>``, ``v_to = q v_from q*``. Its rotation matrix has ``<from>``'s
axes, written in ``<to>``, as its columns.

A document written in ENU gives a wing's frame as the position ``o`` of its origin and the rotation ``Q_KA2ENU``, whose matrix is ``R``. A position ``p`` in ENU is then, in the wing's frame,

.. math::

   p_{KA} = R^T (p_{ENU} - o)

For example, a wing with its origin at ``o = [3, 4, 50]`` and its frame turned 90° about ``z``, ``Q_KA2ENU = [0.7071067811865476, 0, 0, 0.7071067811865476]``, has the point at ``p_ENU = [3, 6, 51]`` at ``p_KA = [2, 0, 1]``: two metres behind its origin along x and one above it.

By convention a structure document places its kite at 90° elevation and 0° heading: straight above the tether exit point, with its leading-to-trailing edge pointing east. A single wing's KA axes are then ENU's and its ``Q_KA2ENU`` is ``[1, 0, 0, 0]``. Several wings on one system each have a frame turned their own way, which their rotations say.

A bearing is a horizontal direction in ENU, the angle from north (``+y``) towards east
(``+x``): north is 0, east is 90. That is clockwise seen from above, a negative
rotation about ``z``. A wind direction is the bearing the wind blows from, so a westerly
wind has direction 270.
