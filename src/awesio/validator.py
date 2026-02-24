from __future__ import annotations

from pathlib import Path, PosixPath, WindowsPath
from referencing import Registry, Resource
from referencing.exceptions import NoSuchResource
import copy
import jsonschema
import jsonschema.validators
import warnings

from .yaml import load_yaml
from .schemas import schemaPath, schema_validation_error_formatter


def retrieve_yaml(uri: str):
    if not uri.endswith(".yaml"):
        raise NoSuchResource(ref=uri)
    uri = uri.removeprefix("src/awesio/")
    path = schemaPath / Path(uri)
    contents = load_yaml(path)
    return Resource.from_contents(contents)


registry = Registry(retrieve=retrieve_yaml)


def _enforce_no_additional_properties(schema):
    """Recursively set additionalProperties: false for all objects in the schema"""
    if isinstance(schema, dict):

        # If this is an object type schema, and additionalProperties is not specified,
        #   set additionalProperties: false
        if (
            schema.get("type") == "object" or "properties" in schema
        ) and "additionalProperties" not in schema:
            schema["additionalProperties"] = False

        # Recursively process all nested schemas
        for key, value in schema.items():
            if key == "properties":
                # Process each property's schema
                for prop_schema in value.values():
                    _enforce_no_additional_properties(prop_schema)
            elif key in ["items", "additionalItems"]:
                # Process array item schemas
                _enforce_no_additional_properties(value)
            elif key in ["oneOf", "anyOf", "allOf"]:
                # Process each subschema in these combining keywords
                for subschema in value:
                    _enforce_no_additional_properties(subschema)
    return schema


def validate(
    input: dict | str | Path, restrictive: bool = True, defaults: bool = False,
) -> None:
    """
    Validates a given AWESIO input by auto-detecting the schema type from metadata.

    Args:
        input (dict | str | Path): Input data as a dictionary or a path to a YAML file 
            containing the data to be validated.
        restrictive (bool, optional): If True, the schema will be modified to enforce
            that no additional properties are allowed. Defaults to True.
        defaults (bool, optional): If True, default values specified in the schema will 
            be applied to the input data during validation. Defaults to False.

    Raises:
        FileNotFoundError: If the schema file corresponding to the schema type is not found.
        TypeError: If the input type is not supported (must be dict, str, or Path-like).
        ValueError: If the schema type cannot be determined from the input data.

    Returns:
        dict: The validated input data. If `defaults` is True, the returned data will 
        include default values specified in the schema. If validation fails, the data
        is still returned but a validation error message is printed.
    """
    if type(input) is dict:
        data = copy.deepcopy(input)
    elif type(input) in [str, Path, PosixPath, WindowsPath]:
        data = load_yaml(input)
    else:
        raise TypeError(f"Input type {type(input)} is not supported.")
    
    # Auto-detect schema_type from metadata
    if "metadata" not in data or "schema" not in data["metadata"]:
        raise ValueError(
            "Schema type could not be automatically determined. "
            "The input data must contain 'metadata.schema' field."
        )
    schema_filename = data["metadata"]["schema"]
    # Remove .yml or .yaml extension to get schema_type
    schema_type = schema_filename.replace(".yml", "").replace(".yaml", "")
    
    schema_file = schemaPath / f"{schema_type}.yaml"
    if not schema_file.exists():
        schema_file = schemaPath / f"{schema_type}.yml"
    if not schema_file.exists():
        raise FileNotFoundError(f"Schema file {schema_file} not found.")

    schema = load_yaml(schema_file)
    if restrictive:
        schema = _enforce_no_additional_properties(schema)

    try:
        if defaults:
            _jsonschema_validate_modified(data, schema, cls = DefaultValidatingDraft7Validator, registry=registry)
        else:
            _jsonschema_validate_modified(data, schema, registry=registry)

        # Additional consistency checks beyond schema validation
        _validate_data_consistency(data, schema_type)
        
    except ValueError as e:
        warnings.warn(f"Validation failed: {e}", UserWarning, stacklevel=2)
        return data

    return data


# See: https://python-jsonschema.readthedocs.io/en/stable/faq/#why-doesn-t-my-schema-s-default-property-set-the-default-on-my-instance
def extend_with_default(validator_class):
    validate_properties = validator_class.VALIDATORS["properties"]

    def set_defaults(validator, properties, instance, schema):
        for property, subschema in properties.items():
            if "default" in subschema:
                instance.setdefault(property, subschema["default"])

        for error in validate_properties(validator, properties, instance, schema):
            yield error

    return jsonschema.validators.extend(validator_class, {"properties": set_defaults})

DefaultValidatingDraft7Validator = extend_with_default(jsonschema.Draft7Validator)

def _jsonschema_validate_modified(instance, schema, cls=None, *args, **kwargs):
    """Modification of the `jsonschema.validate` which is though to provide a better error message when validation fails"""
    if cls is None:
        cls = jsonschema.validators.validator_for(schema)

    cls.check_schema(schema)
    validator = cls(schema, *args, **kwargs)
    schema_validation_error_formatter(validator.iter_errors(instance), schema['$id'])


def _validate_cluster_count(data: dict) -> None:
    """Validates that the number of clusters in metadata matches the actual number of clusters."""
    if "metadata" in data and "n_clusters" in data["metadata"] and "clusters" in data:
        expected_count = data["metadata"]["n_clusters"]
        actual_count = len(data["clusters"])
        if expected_count != actual_count:
            raise ValueError(
                f"Cluster count mismatch: metadata.n_clusters is {expected_count} "
                f"but actual number of clusters is {actual_count}"
            )


def _validate_data_consistency(data: dict, schema_type: str) -> None:
    """Validate data consistency based on schema type."""
    if schema_type == "wind_resource_schema":
        _validate_wind_resource_consistency(data)
    elif schema_type == "power_curves_schema":
        _validate_power_curves_consistency(data)


def _validate_wind_resource_consistency(data: dict) -> None:
    """Validates consistency requirements for wind resource data."""
    # Check cluster count
    _validate_cluster_count(data)
    
    # Check that u_normalized and v_normalized have same length as altitudes
    if "clusters" in data and "altitudes" in data:
        altitude_count = len(data["altitudes"])
        for i, cluster in enumerate(data["clusters"]):
            if len(cluster.get("u_normalized", [])) != altitude_count:
                raise ValueError(
                    f"Cluster {cluster.get('id', i+1)}: u_normalized length ({len(cluster.get('u_normalized', []))}) "
                    f"does not match altitudes length ({altitude_count})"
                )
            if len(cluster.get("v_normalized", [])) != altitude_count:
                raise ValueError(
                    f"Cluster {cluster.get('id', i+1)}: v_normalized length ({len(cluster.get('v_normalized', []))}) "
                    f"does not match altitudes length ({altitude_count})"
                )
            if len(cluster.get("u_normalized", [])) != len(cluster.get("v_normalized", [])):
                raise ValueError(
                    f"Cluster {cluster.get('id', i+1)}: u_normalized and v_normalized arrays must have the same length"
                )
    
    # Check unique cluster IDs and consecutive numbering
    if "clusters" in data:
        cluster_ids = [cluster.get("id") for cluster in data["clusters"]]
        if len(cluster_ids) != len(set(cluster_ids)):
            raise ValueError("Cluster IDs must be unique")
        expected_ids = list(range(1, len(cluster_ids) + 1))
        if sorted(cluster_ids) != expected_ids:
            raise ValueError(f"Cluster IDs must be consecutive starting from 1. Expected {expected_ids}, got {sorted(cluster_ids)}")
    
    # Check wind speed bins consistency
    if "wind_speed_bins" in data and "metadata" in data:
        bins = data["wind_speed_bins"]
        metadata = data["metadata"]
        
        expected_bin_centers = metadata.get("n_wind_speed_bins")
        if expected_bin_centers and "bin_centers_m_s" in bins:
            actual_bin_centers = len(bins["bin_centers_m_s"])
            if actual_bin_centers != expected_bin_centers:
                raise ValueError(
                    f"bin_centers_m_s length ({actual_bin_centers}) does not match n_wind_speed_bins ({expected_bin_centers})"
                )
        
        if "bin_edges_m_s" in bins and "bin_centers_m_s" in bins:
            if len(bins["bin_edges_m_s"]) != len(bins["bin_centers_m_s"]) + 1:
                raise ValueError(
                    f"bin_edges_m_s must have exactly one more element than bin_centers_m_s. "
                    f"Got {len(bins['bin_edges_m_s'])} edges and {len(bins['bin_centers_m_s'])} centers"
                )


def _validate_power_curves_consistency(data: dict) -> None:
    """Validates consistency requirements for power curves data."""
    if not ("power_curves" in data and "altitudes_m" in data and "reference_wind_speeds_m_s" in data):
        return
    
    altitude_count = len(data["altitudes_m"])
    wind_speed_count = len(data["reference_wind_speeds_m_s"])
    
    # Check unique profile IDs
    profile_ids = [curve.get("profile_id") for curve in data["power_curves"]]
    if len(profile_ids) != len(set(profile_ids)):
        raise ValueError("Power curve profile_id values must be unique")
    
    # Check that probability weights sum to approximately 1.0
    total_weight = sum(curve.get("probability_weight", 0) for curve in data["power_curves"])
    if abs(total_weight - 1.0) > 0.001:  # Allow small floating point tolerance
        raise ValueError(f"Sum of probability_weight values should equal 1.0, got {total_weight}")
    
    # Check array length consistency within each power curve
    for i, curve in enumerate(data["power_curves"]):
        profile_id = curve.get("profile_id", i+1)
        
        # Check u_normalized and v_normalized match altitudes
        if "u_normalized" in curve:
            if len(curve["u_normalized"]) != altitude_count:
                raise ValueError(
                    f"Power curve {profile_id}: u_normalized length ({len(curve['u_normalized'])}) "
                    f"does not match altitudes_m length ({altitude_count})"
                )
        if "v_normalized" in curve:
            if len(curve["v_normalized"]) != altitude_count:
                raise ValueError(
                    f"Power curve {profile_id}: v_normalized length ({len(curve['v_normalized'])}) "
                    f"does not match altitudes_m length ({altitude_count})"
                )
        if "u_normalized" in curve and "v_normalized" in curve:
            if len(curve["u_normalized"]) != len(curve["v_normalized"]):
                raise ValueError(
                    f"Power curve {profile_id}: u_normalized and v_normalized arrays must have the same length"
                )
        
        # Check power and time arrays match reference wind speeds
        power_time_arrays = [
            "cycle_power_w", "reel_out_power_w", "reel_in_power_w",
            "reel_out_time_s", "reel_in_time_s", "cycle_time_s"
        ]
        for array_name in power_time_arrays:
            if array_name in curve:
                if len(curve[array_name]) != wind_speed_count:
                    raise ValueError(
                        f"Power curve {profile_id}: {array_name} length ({len(curve[array_name])}) "
                        f"does not match reference_wind_speeds_m_s length ({wind_speed_count})"
                    )