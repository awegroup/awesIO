### Changed

- BREAKING: a structure file's required columns are only what drawing the kite and pairing it with a saved state need; rest lengths, diameters, masses, inertias, tube pressures, a winch's gear ratio and drum radius, and the material columns are optional columns the schema checks by header wherever they stand. The `materials` block is optional, `metadata.connectivity_sha` is required, and pulley `efficiency` is a tool's own column.
- BREAKING: renamed `l0` to `rest_length`, `stations` to `spanwise_stations` and `Q_KA_to_ENU` to `Q_KA2ENU`; rotations are named `Q_<from>2<to>`.
