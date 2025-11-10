# CI/CD Setup Guide

This document explains how to set up the continuous integration and code quality checks for this project.

## Overview

The project uses a GitHub Actions workflow that automatically runs code quality checks on every pull request and push to main branches. The workflow includes:

1. **Ruff Linting** - Fast Python linter and formatter
2. **SonarQube Analysis** - Comprehensive code quality and security analysis

## Workflow Configuration

The workflow is defined in `.github/workflows/code-quality.yml` and runs three jobs:

### 1. Ruff Linting (`lint-with-ruff`)

This job:
- Checks code style and quality using Ruff
- Verifies formatting compliance
- Fails if any linting errors are found

### 2. SonarQube Scan (`sonarqube-scan`)

This job:
- Runs comprehensive code analysis
- Checks for bugs, vulnerabilities, and code smells
- Generates code coverage reports
- Uploads results to SonarQube server
- Waits for Quality Gate validation

### 3. Code Quality Summary (`code-quality-summary`)

This job:
- Runs after all checks complete
- Provides a summary of all quality checks
- Fails the PR if any check failed

## GitHub Repository Setup

### Required Secrets

You need to configure the following secrets in your GitHub repository:

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add:

#### `SONAR_TOKEN`
- Your SonarQube authentication token
- Get this from: SonarQube → My Account → Security → Generate Token
- Example: `sqp_1234567890abcdef...`

#### `SONAR_HOST_URL`
- Your SonarQube server URL
- For local development: `http://localhost:9000`
- For SonarCloud: `https://sonarcloud.io`
- For self-hosted: Your server URL (e.g., `https://sonar.yourcompany.com`)

### Branch Protection Rules

To enforce code quality checks on PRs:

1. Go to **Settings** → **Branches**
2. Add a branch protection rule for `main` (or your default branch)
3. Enable:
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
4. Select these required status checks:
   - `Lint with Ruff`
   - `SonarQube Analysis`
   - `Code Quality Summary`

## Local Development

### Running Ruff Locally

Install Ruff:
```bash
pip install ruff
```

Check your code:
```bash
# Run linter
ruff check .

# Auto-fix issues
ruff check . --fix

# Check formatting
ruff format --check .

# Format code
ruff format .
```

### Running SonarQube Locally

#### Option 1: Using Docker (Recommended)

1. Start SonarQube server:
```bash
docker run -d --name sonarqube -p 9000:9000 sonarqube:latest
```

2. Access SonarQube at http://localhost:9000 (default credentials: admin/admin)

3. Generate a token:
   - Go to My Account → Security → Generate Token
   - Save the token securely

4. Update `sonar-project.properties` with your token

5. Run the scan:
```bash
# Using sonar-scanner
sonar-scanner

# Or using the analyze script
./analyze.sh
```

#### Option 2: Using Installed Scanner

1. Download SonarScanner from https://docs.sonarqube.org/latest/analysis/scan/sonarscanner/

2. Add to PATH or use the bundled version in this project

3. Run:
```bash
./sonar-scanner-7.3.0.5189-windows-x64/bin/sonar-scanner
```

## Ruff Configuration

The project's Ruff configuration is defined in `pyproject.toml`:

- **Line length**: 88 characters (Black-compatible)
- **Target Python**: 3.8+
- **Enabled rules**:
  - E, W: pycodestyle errors and warnings
  - F: pyflakes
  - I: isort (import sorting)
  - N: pep8-naming
  - UP: pyupgrade
  - B: flake8-bugbear
  - C4: flake8-comprehensions
  - SIM: flake8-simplify
  - RUF: ruff-specific rules
  - PLR: pylint refactor
  - S: flake8-bandit (security)
  - T20: flake8-print
  - ERA: eradicate
  - PD: pandas-vet

## SonarQube Configuration

The project's SonarQube configuration is in `sonar-project.properties`:

### Key Settings

- **Project Key**: `practica2-calidadsoft`
- **Python Versions**: 3.8, 3.9, 3.10, 3.11, 3.12
- **Coverage Reports**: `coverage.xml`
- **Quality Gate**: Enabled with 5-minute timeout

### Exclusions

The following directories are excluded from analysis:
- Virtual environments (venv, .venv, myenv)
- Cache directories (__pycache__, .pytest_cache, .ruff_cache, .mypy_cache)
- IDE configurations (.vscode, .idea)
- Build artifacts (dist, build, *.egg-info)
- Git and GitHub directories (.git, .github)
- SonarQube scanner directory

## Workflow Triggers

The workflow runs on:

- **Pull Requests** to main, master, or develop branches
- **Pushes** to main, master, or develop branches

## Troubleshooting

### Ruff Issues

If Ruff checks fail:

1. Run `ruff check . --fix` to auto-fix issues
2. Run `ruff format .` to format code
3. Check `pyproject.toml` for configuration
4. Review the GitHub Actions log for specific errors

### SonarQube Issues

If SonarQube analysis fails:

1. **Authentication Error**:
   - Verify `SONAR_TOKEN` secret is correctly set
   - Generate a new token if needed

2. **Connection Error**:
   - Verify `SONAR_HOST_URL` is correct
   - Check if SonarQube server is accessible

3. **Quality Gate Failure**:
   - Review the SonarQube dashboard
   - Fix identified bugs, vulnerabilities, or code smells
   - Improve code coverage if needed

4. **Project Not Found**:
   - Ensure the project exists in SonarQube
   - Verify `sonar.projectKey` matches your SonarQube project

### Coverage Issues

If coverage is not being reported:

1. Install pytest-cov:
```bash
pip install pytest-cov
```

2. Run tests with coverage:
```bash
pytest --cov=. --cov-report=xml
```

3. Verify `coverage.xml` is generated

## Best Practices

1. **Run checks locally** before pushing:
   ```bash
   ruff check . --fix && ruff format .
   ```

2. **Keep code clean**:
   - Fix all Ruff warnings
   - Address SonarQube issues promptly
   - Maintain high code coverage (>80%)

3. **Review SonarQube reports**:
   - Check for security vulnerabilities
   - Fix code smells and bugs
   - Improve code maintainability

4. **Update dependencies**:
   - Keep Ruff up to date
   - Update SonarQube scanner periodically
   - Review and update pyproject.toml rules

## Additional Resources

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [SonarQube Documentation](https://docs.sonarqube.org/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Python Code Quality Tools](https://realpython.com/python-code-quality/)

## Support

For issues or questions:
- Check GitHub Actions logs for detailed error messages
- Review SonarQube dashboard for code quality insights
- Consult the official documentation linked above
