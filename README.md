# Databricks Asset Bundle — Python Data Engineering - Databricks platform engineering / CI/CD reference implementation.
A practical Databricks Data Engineering project demonstrating how to develop, test, package, deploy, and execute Python workloads using **Databricks Asset Bundles (DAB)** and **GitHub Actions CI/CD**.

The project implements separate **DEV and PROD environments**, Python Wheel packaging, automated testing, parameterized Databricks Jobs, OAuth Service Principal authentication, and a reproducible development environment using VS Code Dev Containers.

---

## Architecture

```text
                         GitHub Repository
                                │
                    ┌───────────┴───────────┐
                    │                       │
                   dev                    prod
                    │                       │
                    ▼                       ▼
             deploy_dev.yml          deploy_prd.yml
                    │                       │
                    ▼                       ▼
             GitHub Actions           GitHub Actions
                    │                       │
              ┌─────┴─────┐           ┌─────┴─────┐
              │           │           │           │
            Tests       Validate     Validate    Deploy
              │           │           │           │
              └─────┬─────┘           └─────┬─────┘
                    │                       │
                    ▼                       ▼
              DAB Bundle              DAB Bundle
                    │                       │
                    ▼                       ▼
             Databricks DEV          Databricks PROD
                    │                       │
                    └───────────┬───────────┘
                                │
                                ▼
                         dab_test_job
                                │
                                ▼
                     demo_notebook.py
                                │
                                ▼
                         Unity Catalog
                     catalog.schema.users
```

---

# Project Overview

This project is based on the **Databricks Asset Bundle default Python project structure** and has been extended to demonstrate a more complete Data Engineering deployment workflow.

The main workload demonstrates:

1. Python application development.
2. Databricks notebook execution.
3. Parameterized Databricks Jobs.
4. Python Wheel packaging.
5. Databricks Asset Bundle configuration.
6. DEV and PROD environments.
7. Automated testing.
8. GitHub Actions CI/CD.
9. OAuth Service Principal authentication.
10. Containerized local development.

---

# Technology Stack

| Technology               | Purpose                                     |
| ------------------------ | ------------------------------------------- |
| Python 3.10–3.12         | Application development                     |
| PySpark                  | Distributed data processing                 |
| Databricks               | Data Engineering platform                   |
| Databricks Asset Bundles | Deployment and resource management          |
| Databricks CLI           | Bundle validation, deployment and execution |
| Unity Catalog            | Catalog/schema/table organization           |
| uv                       | Python dependency management and build      |
| Hatchling                | Python Wheel build backend                  |
| Pytest                   | Automated testing                           |
| Ruff                     | Python linting                              |
| GitHub Actions           | CI/CD                                       |
| Docker                   | Development environment                     |
| VS Code Dev Containers   | Reproducible development environment        |
| YAML                     | Databricks and CI/CD configuration          |
| TOML                     | Python project configuration                |

---

# Repository Structure

```text
.
├── .devcontainer/
│   ├── .env
│   ├── Dockerfile
│   ├── devcontainer.json
│   └── requirements.txt
│
├── .github/
│   └── workflows/
│       ├── deploy_dev.yml
│       └── deploy_prd.yml
│
├── dab_test/
│   ├── .vscode/
│   │
│   ├── fixtures/
│   │
│   ├── resources/
│   │   └── jobs/
│   │       └── dab_test_job.yml
│   │
│   ├── src/
│   │   ├── dab_test/
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   │
│   │   └── notebooks/
│   │       └── demo_notebook.py
│   │
│   ├── tests/
│   │   ├── job_config_test.py
│   │   └── main_test.py
│   │
│   ├── AGENTS.md
│   ├── CLAUDE.md
│   ├── README.md
│   ├── databricks.yml
│   └── pyproject.toml
│
└── README.md
```

---

# Databricks Asset Bundle

The core of the project is the `databricks.yml` file.

The Bundle is named:

```yaml
bundle:
  name: dab_test
```

The configuration includes resource definitions from:

```text
resources/jobs/*.yml
resources/pipelines/*.yml
resources/schemas/*.yml
```

It also defines a Python Wheel artifact:

```yaml
artifacts:
  python_artifact:
    type: whl
    build: uv build --wheel
```

This means the deployment process can build the Python application into a `.whl` package and make it available to the Databricks workload.

---

# Environments

The project defines two Databricks Bundle targets.

## DEV

The `dev` target uses:

```yaml
mode: development
```

and is the default Bundle target.

It uses the following configuration:

```text
Catalog: dev
Schema: rescue_b
```

The DEV workflow is intended for development, testing, validation, deployment, and execution.

---

## PROD

The `prod` target uses:

```yaml
mode: production
```

with:

```text
Catalog: prod
Schema: rescue_b
```

The production deployment is associated with the `prod` Git branch.

The production workflow can be triggered by:

* a push to the `prod` branch;
* manual GitHub Actions execution.

---

# Python Application

The main Python package is located under:

```text
dab_test/src/dab_test/
```

The main application contains a simple Spark workload that reads the Databricks sample NYC Taxi dataset:

```python
def find_all_taxis() -> DataFrame:
    return spark.read.table("samples.nyctaxi.trips")
```

The `main()` function displays the first five records.

The project therefore provides a minimal Python/Spark workload that can be packaged and executed through the Databricks environment.

---

# Demo Notebook

The project also contains:

```text
dab_test/src/notebooks/demo_notebook.py
```

The notebook demonstrates parameterized Databricks execution using widgets:

```text
catalog
user_id
user_name
```

The notebook:

1. Receives runtime parameters.
2. Creates a `users` table if it does not exist.
3. Inserts sample users.
4. Inserts the parameterized user.
5. Reads the resulting table.
6. Displays the resulting DataFrame.

The target table follows the pattern:

```text
<catalog>.rescue_b.users
```

For example:

```text
dev.rescue_b.users
prod.rescue_b.users
```

---

# Databricks Job

The Job is defined in:

```text
dab_test/resources/jobs/dab_test_job.yml
```

The Job is called:

```text
dab_test_job
```

It contains a task named:

```text
ingestao_usuarios
```

which executes:

```text
src/notebooks/demo_notebook.py
```

The Job exposes parameters including:

```text
catalog_name
user_id
user_name
```

This allows the same notebook to be reused with different runtime values instead of hard-coding the input data.

---

# Job Schedule

The Job configuration defines a Quartz cron schedule:

```text
Every Tuesday at 08:00
Timezone: America/Sao_Paulo
```

The Job also has a timeout of:

```text
900 seconds
```

Failure notifications are configured through Databricks Job email notifications.

---

# Dynamic Parameters

One of the main concepts demonstrated by this project is the separation between:

### Bundle variables

Defined in:

```text
databricks.yml
```

Example:

```text
catalog
schema
catalog_name
performance_target
```

and:

### Job parameters

Defined in:

```text
resources/jobs/dab_test_job.yml
```

Example:

```text
catalog_name
user_id
user_name
```

The values can flow through the deployment configuration into the notebook at runtime.

Conceptually:

```text
databricks.yml
      │
      │ ${var.catalog_name}
      ▼
Databricks Job
      │
      │ {{job.parameters.catalog_name}}
      ▼
demo_notebook.py
      │
      ▼
Unity Catalog
```

---

# Python Packaging

The Python project is configured through:

```text
dab_test/pyproject.toml
```

The project supports:

```text
Python >= 3.10
Python < 3.13
```

The build system uses:

```text
Hatchling
```

The Wheel package is built using:

```bash
uv build --wheel
```

The resulting package can be used by the Databricks deployment.

---

# Development Dependencies

The project includes development dependencies for:

* Pytest
* Ruff
* PyYAML
* Databricks DLT
* Databricks Connect
* IPython Kernel

Install the development dependencies using:

```bash
uv sync --dev
```

---

# Testing

Tests are located under:

```text
dab_test/tests/
```

Current test modules include:

```text
main_test.py
job_config_test.py
```

Run the tests locally with:

```bash
uv run pytest
```

The DEV CI/CD workflow also executes:

```bash
uv run pytest -s
```

before Bundle validation and deployment.

---

# CI/CD

The repository contains two GitHub Actions workflows:

```text
.github/workflows/
├── deploy_dev.yml
└── deploy_prd.yml
```

## DEV Pipeline

The DEV workflow is triggered by pushes to:

```text
dev
```

It performs:

```text
Checkout
   │
   ▼
Install Databricks CLI
   │
   ▼
Install uv
   │
   ▼
Configure Databricks OAuth
   │
   ▼
Run Pytest
   │
   ▼
Validate Bundle
   │
   ▼
Deploy Bundle
   │
   ▼
Run Databricks Job
```

---

# PROD Pipeline

The production workflow is triggered by:

```text
push to prod
```

or manually through:

```text
workflow_dispatch
```

The production workflow performs:

```text
Checkout
   │
   ▼
Install Databricks CLI
   │
   ▼
Install uv
   │
   ▼
Configure PROD OAuth Service Principal
   │
   ▼
Validate Bundle
   │
   ▼
Deploy Bundle
   │
   ▼
Run Databricks Job
```

The PROD workflow deploys using:

```bash
databricks bundle deploy --target prod
```

and executes:

```bash
databricks bundle run dab_test_job --target prod
```

---

# Authentication

GitHub Actions authenticates to Databricks using an **OAuth Service Principal**.

The workflows obtain the following values from GitHub Secrets:

```text
DATABRICKS_HOST
DATABRICKS_CLIENT_ID
DATABRICKS_CLIENT_SECRET
```

Environment-specific secrets are used for DEV and PROD.

For example:

```text
DATABRICKS_HOST_DEV
DATABRICKS_CLIENT_ID_DEV
DATABRICKS_CLIENT_SECRET_DEV
```

and:

```text
DATABRICKS_HOST_PRD
DATABRICKS_CLIENT_ID_PRD
DATABRICKS_CLIENT_SECRET_PRD
```

No credentials should be committed to the repository.

---

# Local Development

## Prerequisites

Recommended tools:

* Git
* Docker
* Visual Studio Code
* VS Code Dev Containers extension
* Python 3.10–3.12
* uv
* Databricks CLI

---

## Dev Container

The project provides a development container under:

```text
.devcontainer/
```

with:

```text
Dockerfile
devcontainer.json
requirements.txt
.env
```

Open the repository in VS Code and select:

```text
Dev Containers: Reopen in Container
```

This provides a reproducible development environment.

> Never commit production credentials, access tokens, client secrets, or other sensitive information to `.env` or the repository.

---

# Databricks CLI

Authenticate to Databricks using your preferred authentication method.

For a local profile:

```bash
databricks configure
```

Verify the CLI:

```bash
databricks --version
```

---

# Validate the Bundle

From the project directory:

```bash
cd dab_test
```

Validate DEV:

```bash
databricks bundle validate --target dev
```

Validate PROD:

```bash
databricks bundle validate --target prod
```

Validation should be performed before deployment.

---

# Deploy to DEV

```bash
cd dab_test

databricks bundle deploy --target dev
```

After deployment, execute the Job:

```bash
databricks bundle run dab_test_job --target dev
```

---

# Deploy to PROD

Production deployment should preferably occur through the GitHub Actions workflow.

The equivalent CLI commands are:

```bash
cd dab_test

databricks bundle validate --target prod

databricks bundle deploy --target prod

databricks bundle run dab_test_job --target prod
```

---

# End-to-End Deployment Flow

The complete workflow is:

```text
Developer
    │
    │ git push
    ▼
GitHub
    │
    ├───────────────┐
    │               │
   dev             prod
    │               │
    ▼               ▼
DEV Workflow    PROD Workflow
    │               │
    ▼               ▼
Pytest          Validation
    │               │
    ▼               ▼
Validation      Deployment
    │               │
    ▼               ▼
Deployment      Job Execution
    │               │
    ▼               ▼
Databricks DEV  Databricks PROD
```

---

# Configuration Files

## `databricks.yml`

Defines the Databricks Asset Bundle.

Responsible for:

* Bundle name
* Resources
* Variables
* Artifacts
* DEV target
* PROD target
* Workspace configuration

---

## `pyproject.toml`

Defines the Python project.

Responsible for:

* Python version
* Project metadata
* Dependencies
* Development dependencies
* Entry point
* Build system
* Wheel packaging
* Ruff configuration

---

## `resources/jobs/dab_test_job.yml`

Defines the Databricks Job.

Responsible for:

* Job name
* Job parameters
* Schedule
* Timeout
* Notifications
* Notebook task
* Runtime parameters
* Performance configuration

---

## `.github/workflows/deploy_dev.yml`

Defines the DEV CI/CD pipeline.

Responsible for:

* Installing tooling
* Authentication
* Running tests
* Bundle validation
* Deployment
* Job execution

---

## `.github/workflows/deploy_prd.yml`

Defines the PROD CI/CD pipeline.

Responsible for:

* Installing tooling
* PROD authentication
* Bundle validation
* Production deployment
* Job execution

---

# Key Engineering Concepts

This project demonstrates the following Data Engineering and DevOps practices:

### Infrastructure as Code

Databricks resources are defined as code rather than being created manually through the Databricks UI.

### Environment Separation

The same Bundle supports:

```text
DEV
PROD
```

using different targets.

### Python Packaging

The application is packaged as a Python Wheel before deployment.

### Automated Testing

Pytest is integrated into the DEV deployment pipeline.

### CI/CD

GitHub Actions automates the deployment lifecycle.

### Parameterized Workloads

The Databricks Job passes runtime parameters into the notebook.

### Service Principal Authentication

CI/CD uses OAuth-based Service Principal authentication rather than personal credentials.

### Reproducible Development

The Dev Container provides a consistent development environment.

---

# Project Status

Current implementation:

* [x] Databricks Asset Bundle
* [x] Python project structure
* [x] PySpark application
* [x] Databricks notebook
* [x] Parameterized Databricks Job
* [x] Unity Catalog catalog/schema configuration
* [x] DEV target
* [x] PROD target
* [x] Python Wheel packaging
* [x] uv dependency management
* [x] Hatchling build system
* [x] Pytest tests
* [x] Ruff configuration
* [x] VS Code Dev Container
* [x] GitHub Actions DEV pipeline
* [x] GitHub Actions PROD pipeline
* [x] Databricks OAuth Service Principal authentication
* [x] Automated Databricks Job execution

---

# Future Improvements

Potential extensions include:

* [ ] Add Delta Lake ingestion and transformation layers
* [ ] Add Bronze/Silver/Gold architecture
* [ ] Add data quality validation
* [ ] Add integration tests against Databricks
* [ ] Add structured logging
* [ ] Add monitoring and alerting
* [ ] Add Unity Catalog permissions management
* [ ] Add CI quality gates for Ruff
* [ ] Add pull-request validation
* [ ] Add deployment approval gates for PROD
* [ ] Add infrastructure documentation
* [ ] Add job run monitoring
* [ ] Add data lineage documentation

---

# Learning Objectives

This project was created to demonstrate practical knowledge of:

```text
Python
  │
  ├── Packaging
  ├── Testing
  └── PySpark
        │
        ▼
   Databricks
        │
        ├── Asset Bundles
        ├── Jobs
        ├── Notebooks
        └── Unity Catalog
        │
        ▼
      DevOps
        │
        ├── Git
        ├── GitHub Actions
        ├── CI/CD
        └── Service Principal
```

The main objective is to demonstrate how a Data Engineering workload can move from **local development to a controlled production deployment** using modern software engineering practices.

---

# Author

**Ruben Cruz**

Data Engineering · Data Integration · Python · PySpark · Databricks · CI/CD
