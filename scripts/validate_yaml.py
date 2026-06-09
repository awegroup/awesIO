"""
Validate YAML configuration files using awesIO schemas.

Usage:
    Edit the FILES_TO_VALIDATE list below, then run:
    python validate_yaml.py
"""

import sys
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
    "examples/system_config/fixed_wing_multiple_tether_GG_system.yml"
]
# ============================================================================


def main():
    # Convert to Path objects
    file_paths = [Path(f) for f in FILES_TO_VALIDATE]
    
    # Validate each file
    results = []
    for file_path in file_paths:
        if not file_path.exists():
            print(f"\n[FAIL] File not found: {file_path}")
            results.append((file_path, False))
            continue
            
        print(f"\nValidating: {file_path}")
        data = validate(file_path)
        schema_name = data["metadata"]["schema"]
        print(f"Schema: {schema_name}")
        results.append((file_path, True))

if __name__ == "__main__":
    main()
