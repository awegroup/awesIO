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
        if (schema.get("type") == "object" or "properties" in schema
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
    input: dict | str | Path, restrictive: bool = False,
) -> None:
    """
    Validates a given AWESIO input by auto-detecting the schema type from metadata.

    Args:
        input (dict | str | Path): Input data as a dictionary or a path to a YAML file 
            containing the data to be validated.
        restrictive (bool, optional): If True, the schema will be modified to enforce
            that no additional properties are allowed. Defaults to False.

    Raises:
        FileNotFoundError: If the schema file corresponding to the schema type is not found.
        TypeError: If the input type is not supported (must be dict, str, or Path-like).
        ValueError: If the schema type cannot be determined from the input data.

    Returns:
        dict: The validated input data. If validation fails, the data
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
        _jsonschema_validate_modified(data, schema, registry=registry)
        
    except (ValueError, jsonschema.ValidationError) as e:
        warnings.warn(f"Validation failed: {e}", UserWarning, stacklevel=2)
        return data

    return data


def _jsonschema_validate_modified(instance, schema, cls=None, *args, **kwargs):
    """Modification of the `jsonschema.validate` which is though to provide a better error message when validation fails"""
    if cls is None:
        cls = jsonschema.validators.validator_for(schema)

    cls.check_schema(schema)
    validator = cls(schema, *args, **kwargs)
    schema_validation_error_formatter(validator.iter_errors(instance), schema['$id'])