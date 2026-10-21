AWE System Structure Schema
===========================

The structure schema describes the **resolved structural definition** of an AWE
system: the points, the segments, pulleys, tethers and winches built on them, the
wings with their stations and canopy faces, the rigid bodies, and the tubes between
those bodies. What a block requires is what drawing the system and pairing it with a
saved state need. What a solver needs beyond that — rest lengths, masses, materials —
is in optional columns the schema defines once, so one file serves a viewer and a
solver alike.

It is the layer :doc:`system_schema` leaves free-form — its ``wing_sections``,
``bridle_nodes``, ``bridle_lines`` and ``bridle_connections`` blocks are bare
``type: object`` under ``additionalProperties: true``, so today any content
validates.

Plotting is the clearest symptom of not having it. Two tools cannot draw each other's
system because neither can describe it, so every viewer is written against one model.
With a shared structure, drawing a state is one code path and every model gets every
viewer.

Validation, units, versioning and a tool's own blocks follow the :doc:`conventions`
every awesIO file shares.

Canonical form only
-------------------

A conforming file is **fully resolved and expanded**: no variable substitution block,
no segment counts left to expand, every component explicit. It is readable with
nothing beyond a YAML or JSON parser.

Authoring dialects — multi-variable substitution, tether expansion, defaults — stay
profiles of the tool that defines them and *emit* canonical files. An interchange
format is worth having only if any tool can read it, and requiring implementers to
build a substitution engine before they can load a file is an adoption barrier.
Draft-07 could not express an authoring layer in any case: a row whose arity depends
on a variables block has no vocabulary in JSON Schema.

Tables, not nesting
-------------------

Every block is a ``headers``/``units``/``data`` table and every reference is by name,
so a file reads as a spreadsheet and rows reorder without rewriting indices:

.. code-block:: yaml

   segments:
     headers: [name, points, rest_length, diameter, material]
     units: [-, -, m, m, -]
     data:
       - [seg_1, [ground, tether_1], 10.0, 0.004, dyneema]

What an element connects is one column holding a tuple of distinct names — two for a
segment's ``points``, a pulley's ``segments`` and a tube's ``bodies``, three or four
for a canopy face's ``points`` — so the schema fixes how many there are.

The ``units`` row says which unit each column is in, so a file reads without the
schema beside it. A block pins the unit of every column it requires or defines, SI
throughout and spelled as the :doc:`conventions` list them, and a tool's own column
states its own.

Every header is a distinct string and every unit a string, and the units and every row
are exactly as long as the headers. The ``table`` definition states this as
``rowsMatchHeaders``, and a block's optional columns as ``optionalColumns``: keywords
``awesio.validator`` enforces and other draft-07 validators skip.

YAML and JSON are two encodings of one model. JSON is the machine encoding, and it
travels in the table-level metadata of an Arrow state log under the key ``topology``,
which is what makes a log self-describing: plotting it needs no sidecar file.

What a file holds
-----------------

The schema's own description, under *Schema Structure* below, says what a column or block can be: the core, an awesIO column, a material or a tool's own. SAM appends its own wing columns to ``wings``, and its ``transforms`` and ``groups`` ride beside the core as blocks of its own, while ``metadata`` and a table's own keys stay closed.

Materials and their laws
------------------------

A segment, a tube and a wing's canopy may name a row of ``materials`` in their
optional ``material`` or ``canopy_material`` column, rather than carry a stiffness of
their own. A solver needs the materials to build the elements; a viewer does not, so
a file may leave out the materials and the columns naming them. A material is a stiffness ``law`` and that law's ``parameters``,
one mapping in one cell:

.. code-block:: yaml

   materials:
     headers: [name, law, parameters]
     units: [-, -, -]
     data:
       - [dyneema, linear, {density: 970.0, youngs_modulus: 5.5e+10}]
       - [ripstop, membrane, {areal_density: 0.17, membrane_stiffness: 1000.0}]

The schema defines the laws more than one tool implements: ``linear`` for a line,
``membrane`` for canopy fabric and ``breukels2011`` for an inflated tube. Each fixes
the names and units of its parameters and states the curve they describe, so
a reader that has never met the law evaluates it from the schema alone.
``breukels2011`` carries its nineteen correlation constants rather than standing for
them. Any other law is free: its name is a model its readers implement, which fixes
its parameters, and the file still carries every number that model needs. A reader
that does not implement a material's law fails on the elements naming it rather than
substituting another.

Wings, their stations and their canopy
---------------------------------------

A document may hold several wings, so each station and each canopy face names the
``wings`` row it belongs to.

A **station**, a row of ``spanwise_stations``, is a chordwise section of a wing, given by its points. They give the
local chord, from which a reader derives the section's angle of attack and, where
they trace the profile, its airfoil shape. How the aerodynamic load reaches the
points is the reader's coupling.

A station's **local twist** is the angle its chord has turned through about the wing's
KA y axis from where the document places it, positive pitching the leading edge up.

A station is not tied to the aerodynamic mesh: it may cover several of its panels.
A wing's station rows run from +y to -y of its KA frame, left tip to right tip.

**A canopy is fabric meshed over existing points**, the way a ``.obj`` meshes faces
over its vertices: its corners are rows of ``points``, never a second kind of point,
so a bridle line ends on the same point the fabric does. A wing has at most one
canopy, and its ``canopy_material`` is the one fabric all of it is made of, or null
where it has none; each ``canopy_faces`` row is a triangle or quadrilateral of that
canopy, its corners in order around it. What the fabric weighs and how it stretches,
per unit area, belong to its material. Like a tube, a face names what it is rather
than how it is modelled: a reader carries its load as a membrane or as springs along
its edges.

Bodies, and the tubes between them
----------------------------------

A rigid body has a position and a frame: ``pos_ENU`` is its origin, the centre of
its own mass, and ``Q_KA2ENU`` the rotation from its own KA frame into the world.
``extra_mass`` and ``extra_inertia_KA`` are taken about that origin.

Every mass in a document is extra mass, never a total: a reader adds what it
derives. A point's ``extra_mass`` leaves out its segments and canopy faces. A reader
adds half of each attached segment's mass, from its ``diameter``, its ``rest_length`` and its
material's density, and an equal share of each face the point is a corner of: the
face's area times its material's areal density. A face's area is half the norm of
the cross product of its diagonals, or of two edges for a triangle, which holds for
a quadrilateral whose corners are not in one plane. A body's ``extra_mass`` and
``extra_inertia_KA`` leave out the points fixed to it, which a reader adds to the
body.

``extra_inertia_KA`` is the full tensor in the body's KA axes. Where those are its
principal axes the tensor is diagonal; a wing body's KA axes are fixed by the wing's
geometry, so its tensor in general is not.

**A tube joins two bodies**, named in its ``bodies`` column and never as points.
Their positions fix its ends and so its rest length, and one ``diameter`` holds for
the whole element. How it curves between those ends belongs to the element: a
Timoshenko beam carries curvature of its own, and only a shape its material's law
cannot hold — or a taper — needs a chain of tubes.

Pairing with a state log
------------------------

``metadata.connectivity_sha`` guards the pairing of a structure with a state log,
so every file gives it. Its preimage is spelled out on ``metadata.connectivity_sha``
in the schema below; the row numbers in it are **one-based**, so that a zero-based
reader does not see every file as a mismatch.

Frames
------

A column's suffix names the frame of its vectors, ``_ENU`` or ``_KA``, as the
:doc:`conventions` define them. Every position is in ENU, where the system is placed:
a document is expanded all the way into the world, so a reader needs no transform to
draw it.

A body's ``_KA`` frame holds the axes its ``extra_inertia_KA`` is stated in. A control
unit or a single tube has no leading edge to orient it by, so its writer
orients that frame as it likes and ``Q_KA2ENU`` is where the file says which
orientation it chose.

**Each wing says where its own frame is.** A ``wings`` row's ``pos_ENU`` is the origin of the wing's KA frame, a position that need not be a point, and its ``Q_KA2ENU`` the frame's orientation. That is the frame the tools that design a kite draw it in and its aerodynamic mesh is drawn in, so several wings of one shape share one mesh, and a reader takes positions into it as the :doc:`conventions` define. By convention the kite is placed at 90° elevation and 0° heading, so a single wing's rotation is the identity. Where and how a kite is flown is state, and not stated here.

What is not described here
--------------------------

Live state: how positions, velocities, forces, twist angles and reel-out lengths move
from where the document places them. A structure is written once; state is written
every step, which is why it belongs in the columns of a log rather than in this
document.

Examples
--------

``examples/structure`` holds two models of the same kite — the TU Delft V3, a bridled
soft wing, placed straight above its ground anchor. They share the bridle, the tether and the single
winch, and differ in what carries the wing:

``v3_psm_structure.yml``
   The particle lattice: 44 points, 68 segments and 6 pulleys carry the wing's shape,
   and its mass sits on those points. Nine canopy faces span the leading and trailing
   edges between the struts. No bodies and no tubes — the lattice *is* the structure.

``v3_beam_structure.yml``
   The beam wing: 22 rigid bodies, twelve down the leading-edge tube and ten down the
   trailing edge, joined by eleven ``le_beam_*`` tubes along the leading edge and ten
   ``strut_beam_*`` from front to back. The canopy is 90 faces over the tube points
   and 110 ``wing_ctrl_*`` points, the 20 at the tubes riding on their bodies. Under
   them the bridle and one tether, in a document of 220 points over 95 segments. The
   bridle's 40 attachment points each ride on a body of the nearest tube, within
   0.13 m of it; V3Kite carries them and the ``wing_ctrl_*`` points on a massless
   frame of SymbolicAWEModels.jl's own, which the document leaves out.

``v3_canopy`` stands in for V3Kite's canopy springs: their 1000 N/m is its
``membrane_stiffness``, and its ``areal_density`` is zero because the wing's
``extra_mass`` already holds the 170 g/m² fabric of awegroup/TUDELFT_V3_KITE, as
V3Kite carries it. ``v3_tube`` holds the Breukels constants SymbolicAWEModels.jl
evaluates.

Columns
-------

The columns each block requires, in the order its ``headers`` must list them, then
the optional columns it defines, which may stand anywhere after them. Each comes with
the unit its ``units`` row must give it.

.. schema-columns:: ../../src/awesio/schemas/structure_schema.yml

Schema Structure
----------------

.. jsonschema:: ../../src/awesio/schemas/structure_schema.yml
   :auto_reference:
