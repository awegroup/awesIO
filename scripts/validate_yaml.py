"""
Validate YAML configuration files using awesIO schemas.

Usage:
    Edit the FILES_TO_VALIDATE list below, then run:
    python validate_yaml.py
"""

import sys
import warnings
from pathlib import Path

# Add src to path to import awesio
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from awesio.validator import validate


# ============================================================================
# FILES TO VALIDATE - Edit this list to add/remove files
# ============================================================================
FILES_TO_VALIDATE = [
    "examples/wind_resource.yml",
    "examples/ground_gen/soft_kite_pumping_ground_gen_operational_constraints.yml",
    "examples/ground_gen/soft_kite_pumping_ground_gen_power_curves.yml",
    "examples/system_config/soft_kite_pumping_ground_gen_system.yml",
    "examples/system_config/fixed_wing_multiple_tether_GG_system.yml",
    "examples/structure/v3_beam_structure.yml",
    "examples/structure/v3_psm_structure.yml",
]
# ============================================================================


def main():
    """Validate every listed file, then exit non-zero if any of them failed."""
    results = []
    for file_path in [Path(f) for f in FILES_TO_VALIDATE]:
        if not file_path.exists():
            print(f"\n[FAIL] File not found: {file_path}")
            results.append(False)
            continue

        print(f"\nValidating: {file_path}")
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always", UserWarning)
            data = validate(file_path)
        for warning in caught:
            print(f"[FAIL] {warning.message}")
        print(f"Schema: {data['metadata']['schema']}")
        results.append(not caught)

    failed = results.count(False)
    print(f"\n{len(results) - failed} of {len(results)} files valid.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
