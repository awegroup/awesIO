# awesIO

Input/output standard for airborne wind energy systems.

awesIO provides JSON Schema-based validation for AWE system configurations and was developed in the context of IEA Wind Task 48. The terminology/ontology used follows the Airborne Wind Europe Glossary: https://airbornewindeurope.org/glossary-2

Documentation: https://awegroup.github.io/awesIO/



## Available Schemas

Currently includes schemas for:
- Complete airborne systems
- Power curves
- Wind resource data
- Operational constraints


## Installation

### Installation using pixi and git

Install pixi: https://github.com/prefix-dev/pixi?tab=readme-ov-file#installation

Fetch the latest version from git:
```bash
git clone https://github.com/awegroup/awesIO
cd awesIO
```
Run the default validation:
```bash
pixi run validate
```
This will install all of the required Python packages and validate the example files against the included schema files.

### Install Directly from Git Repository using pip

Install the latest version from the main branch without cloning:

```bash
pip install git+https://github.com/awegroup/awesIO.git
```

Install from a specific branch:

```bash
pip install git+https://github.com/awegroup/awesIO.git@branch-name
```

Install from a specific commit or tag:

```bash
pip install git+https://github.com/awegroup/awesIO.git@commit-hash
pip install git+https://github.com/awegroup/awesIO.git@v0.1.0
```

**Using in a Conda environment:**

```bash
conda activate your_environment
pip install git+https://github.com/awegroup/awesIO.git
```

## Usage

After installation, you can import and use awesIO:

```python
from awesio.validator import validate

# Validates YAML file (auto-detects schema from file metadata)
data = validate("path/to/config.yml")
```

## Examples

Example YAML configuration files are available in the `examples/` directory.

### Developers

Clone the repo, then install dev dependencies:

```bash
pip install -e .
pip install -r docs/requirements.txt
```

For the developer guide check: https://awegroup.github.io/awesIO/developer_guide
