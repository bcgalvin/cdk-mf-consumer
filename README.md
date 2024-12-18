# cdk-mf-consumer


A CDK-based infrastructure project demo for integrating flows with external events via CDK.



## Development with Hatch

This project uses [Hatch](https://hatch.pypa.io/) for environment and dependency management. Here's how to use the available environments and scripts:

### Default Environment

The default environment contains core project dependencies and Metaflow flow scripts.

```console
# Activate default environment
hatch shell

# Run Metaflow flows
hatch run ingest_flow  # Run data ingestion flow
```

### Lint Environment

Used for code quality checks and formatting.

```console
# Run all checks
hatch run lint:check

# Individual checks
hatch run lint:check_simple  # Basic mypy checks
hatch run lint:check_pylint  # Pylint checks

# Format code
hatch run lint:format  # Runs black, ruff, and isort
```

### Test Environment

Dedicated environment for running tests.

```console
# Run all tests
hatch run tests:run

# Run specific tests
hatch run tests:run tests/specific_test.py
```

### Infrastructure Environment

Manages AWS CDK infrastructure code.

```console
# Run CDK commands
hatch run infra:cdk synth
hatch run infra:cdk deploy

# Run infrastructure tests
hatch run infra:test
```

## Project Structure

```
cdk-mf-consumer/
├── infrastructure/       # AWS CDK infrastructure code
│   ├── app.py           # CDK app entry point
│   └── infrastructure/  # Stack definitions
├── src/
│   └── cdk_mf_consumer/
│       ├── flows/       # Metaflow pipeline definitions
│       ├── models/      # Pydantic data models
│       ├── api.py       # API client interfaces
│       ├── client.py    # Client implementations
│       ├── data.py      # Data processing utilities
│       └── utils.py     # Common utilities
└── tests/               # Test suite
```

## Environment Details

| Environment | Purpose | Key Features |
|-------------|---------|--------------|
| default | Core functionality | - Metaflow flows<br>- Project dependencies |
| lint | Code quality | - Type checking<br>- Style formatting<br>- Linting |
| tests | Testing | - PyTest execution<br>- Coverage reports |
| infra | AWS Infrastructure | - CDK commands<br>- Infrastructure tests |


