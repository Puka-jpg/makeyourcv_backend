# Setup & Contributing

We welcome contributions to RenderCV! This guide will help you set up your development environment.

## Prerequisites

- **Python** 3.12 or higher.
- **uv**: We use `uv` for dependency management.
- **Just**: We use `just` as a command runner.

### Install `uv`
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Install `just`
```bash
cargo install just
# OR
pip install just
```

## Setting Up

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/rendercv/rendercv.git
    cd rendercv
    ```

2.  **Sync dependencies**:
    This will create a virtual environment and install all dev dependencies.
    ```bash
    just sync
    ```

## Development Workflow

We use `just` to run common tasks.

### Running Tests
To run the test suite (pytest):
```bash
just test
```

To run tests with coverage:
```bash
just test-coverage
```

### Formatting & Linting
We use **Black** for formatting and **Ruff** for linting.

Format code:
```bash
just format
```

Run checks (Linting + Type Checking):
```bash
just check
```

### Building Documentation
The documentation (this site) is built with **MkDocs**.

Build docs:
```bash
just build-docs
```

Serve docs locally:
```bash
just serve-docs
```

## Project Management

### Logic Updates
If you change the source code, please ensure you add tests in `tests/`.

### Schema Updates
If you modify the Pydantic models in `src/rendercv/schema`, run the schema update script to regenerate the JSON schema:
```bash
just update-schema
```

### Examples Updates
If you modify the logic that affects output, regenerate the examples:
```bash
just update-examples
```
