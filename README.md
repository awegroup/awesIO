<p align="left">
  <img src="docs/logo/Final%20logo%20awesIO.svg" alt="awesIO Logo" width="200">
</p>

# awesIO

Input/output standard for airborne wind energy systems.

awesIO provides JSON Schema-based validation for AWE system configurations and was developed in the context of IEA Wind Task 48. The terminology/ontology used follows the Airborne Wind Europe Glossary: https://airbornewindeurope.org/glossary-2

[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://awegroup.github.io/awesIO/)



## Available Schemas

Currently includes schemas for:
- Complete airborne systems
- Power curves
- Wind resource data
- Operational constraints


## Installation for users using pip and pixi

Install the latest version from the main branch without cloning:

```bash
pip install git+https://github.com/awegroup/awesIO.git

pixi add --pypi "awesio @ git+https://github.com/awegroup/awesIO.git"

```

Install from a specific branch:

```bash
pip install git+https://github.com/awegroup/awesIO.git@branch-name

pixi add --pypi "awesio @ git+https://github.com/awegroup/awesIO.git@branch-name"

```

Install from a specific commit or tag:

```bash
pip install git+https://github.com/awegroup/awesIO.git@commit-hash
pip install git+https://github.com/awegroup/awesIO.git@v0.1.0

pixi add --pypi "awesio @ git+https://github.com/awegroup/awesIO.git@commit-hash"
pixi add --pypi "awesio @ git+https://github.com/awegroup/awesIO.git@v0.1.0"
```

## Usage

After installation, you can import and use awesIO:

```python
from awesio.validator import validate

# Validates YAML file (auto-detects schema from file metadata)
data = validate("path/to/config.yml")
```

You can also add the ``restrictive=True`` option to enforce that no additional properties are allowed beyond those defined in the schema. This can help catch typos or unintended fields in your YAML files.

## Installation for developers

Fetch the latest version from git:
```bash
git clone https://github.com/awegroup/awesIO
cd awesIO
```
### pip

```bash
pip install -e .
pip install -r docs/requirements.txt
```

## Examples

Example YAML configuration files are available in the `examples/` directory.

## Contributing

Please check the developer guide in the documentation:

[![Developer Guide](https://img.shields.io/badge/developer%20guide-GitHub%20Pages-green)](https://awegroup.github.io/awesIO/source/developer_guide.html)

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
