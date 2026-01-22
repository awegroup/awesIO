<p align="left">
  <img src="docs/logo/Final%20logo%20awesIO.svg" alt="awesIO Logo" width="200">
</p>

# awesIO

Input/output standard for airborne wind energy systems.

awesIO provides JSON Schema-based validation for AWE system configurations and was developed in the context of IEA Wind Task 48. The terminology/ontology used follows the Airborne Wind Europe Glossary: https://airbornewindeurope.org/glossary-2

<p align="left">
  <a href="https://awegroup.github.io/awesIO/">
    <img src="https://img.shields.io/badge/📖_Documentation-View_Docs-blue?style=for-the-badge" alt="Documentation">
  </a>
</p>



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

### pixi
Run the default validation:
```bash
pixi run validate
```
This will install all of the required Python packages and validate the example files against the included schema files.

## Examples

Example YAML configuration files are available in the `examples/` directory.

## Contributing

Please check the developer guide in the documentation:

<p align="left">
  <a href="https://awegroup.github.io/awesIO/developer_guide">
    <img src="https://img.shields.io/badge/👨‍💻_Developer_Guide-Contribute-green?style=for-the-badge" alt="Developer Guide">
  </a>
</p>
