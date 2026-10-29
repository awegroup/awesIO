### Added

- A soft kite's `control_system` may carry an onboard wind turbine in an optional `turbine` block: `name`, `type` (`horizontal_axis_turbine`), `version` and a `structure` with `rotor_diameter`, `mass` and `position_KA` required, and `number_of_blades` and `rated_power` optional. The turbine's mass is its own, not part of the control unit's `structure.mass`. `position_KA` is the rotor hub in the kite's KA frame, whose origin is the control unit, so a turbine on top of the unit has z > 0 and a hanging one z < 0.
