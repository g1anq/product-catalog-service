# SonarQube Integration Guide

## Overview

This guide covers the setup and integration of SonarQube for continuous code quality analysis in the Product Catalog Service project. SonarQube is configured to check code quality, maintainability, security, and reliability metrics.

## Table of Contents

1. [Local SonarQube Setup](#local-sonarqube-setup)
2. [SonarQube Configuration](#sonarqube-configuration)
3. [Quality Gates](#quality-gates)
4. [CI/CD Integration](#cicd-integration)
5. [Using the System](#using-the-system)
6. [Troubleshooting](#troubleshooting)

---

## Local SonarQube Setup

### Prerequisites

- Docker and Docker Compose installed
- Python 3.13+ for local analysis
- Git

### Task 3.1: Docker Setup

#### Step 1: Start SonarQube

```bash
# Start SonarQube with PostgreSQL database
./scripts/sonarqube.sh setup

# Or manually
docker-compose -f docker-compose.sonarqube.yml up -d
```

#### Step 2: Access SonarQube

- URL: http://localhost:9000
- Default Username: `admin`
- Default Password: `admin` (change on first login)

#### Verification

```bash
# Check if SonarQube is running
curl http://localhost:9000/api/system/health
```

**Expected Response:**
```json
{"status":"UP","nodes":[{"name":"node1","host":"sonarqube","port":9001,"status":"UP"}]}
```

---

## SonarQube Configuration

### Task 3.2: Scanner Setup

#### File: `sonar-project.properties`

This file contains critical configuration for Python code analysis:

```properties
# Project Identification
sonar.projectKey=product-catalog-service
sonar.projectName=Product Catalog Service
sonar.projectVersion=1.0.0

# Source locations
sonar.sources=app              # Main application code
sonar.tests=tests              # Test files location

# Python-specific settings
sonar.python.version=3.13      # Python version in use
sonar.python.coverage.reportPaths=coverage.xml  # Coverage report location

# Exclusions
sonar.exclusions=**/migrations/**,**/__pycache__/**,**/.*/**,.venv/**,venv/**
sonar.coverage.exclusions=**/*test*.py,**/tests/**
```

#### Create SonarQube Project

1. Login to http://localhost:9000
2. Click "Create Project" → "Manually"
3. Project Key: `product-catalog-service`
4. Project Name: `Product Catalog Service`
5. Click "Set Up"

#### Generate Authentication Token

1. Go to Profile (top right) → Account
2. Click "Security" tab
3. Under "Tokens", enter name: `github-actions`
4. Click "Generate"
5. Copy token (save in secure location)

#### Configure in GitHub

Store the token as GitHub secret:

1. Go to GitHub Repository → Settings → Secrets and Variables → Actions
2. Create new secret:
   - Name: `SONAR_TOKEN`
   - Value: `<token-from-SonarQube>`
   - Name: `SONAR_HOST_URL`
   - Value: `https://sonarqube.example.com` (or your SonarQube URL)

---

## Quality Gates

### Task 3.3: Quality Gate Configuration

#### Define Quality Gate Conditions

1. Administration → Configuration → Quality Gates
2. Create New Quality Gate: `Product Catalog Gate`
3. Add Conditions:

| Condition | Operator | Value | Apply To |
|-----------|----------|-------|----------|
| Coverage on New Code | >= | 80% | New Code |
| Duplicated Lines on New Code | <= | 3% | New Code |
| Maintainability Rating | is | A | Overall Code |
| Reliability Rating | is | A | Overall Code |
| Security Rating | is | A | Overall Code |
| Security Hotspots Reviewed | >= | 100% | New Code |
| Blocker Issues | = | 0 | Overall Code |
| Critical Issues | = | 0 | Overall Code |

#### Set as Default Quality Gate

1. Go to Quality Gates
2. Click on "Product Catalog Gate"
3. Click "Set as Default"

#### Assign to Project

1. Administration → Projects → Select Project
2. Quality Gate: `Product Catalog Gate`

#### "Clean as You Code" Principle

Configure New Code Definition:

1. Administration → Projects → Select Project
2. New Code Definition: `Since previous version`
3. This ensures analysis focuses on recently changed code

---

## CI/CD Integration

### Task 3.4: GitHub Actions Integration

#### Pipeline Flow

```
lint (flake8)
  ↓
test (pytest + coverage)
  ↓
sonarqube (SonarQube analysis) ← Quality Gate check
  ↓
build (Docker build & push) ← Only if QG passes
```

#### SonarQube Stage Configuration

The `.github/workflows/devops-pipeline.yml` includes:

```yaml
sonarqube:
  needs: test
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.13'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt

    - name: Generate coverage report
      run: |
        pytest --cov=app --cov-report=xml tests/

    - name: SonarQube Scan
      uses: SonarSource/sonarqube-scan-action@master
      env:
        SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
        SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}

    - name: SonarQube Quality Gate Check
      uses: SonarSource/sonarqube-quality-gate-action@master
      env:
        SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

#### Required GitHub Secrets

```
SONAR_TOKEN     = <SonarQube authentication token>
SONAR_HOST_URL  = <SonarQube server URL>
```

---

## Using the System

### Local Analysis

#### Prerequisites

```bash
# Install Python dependencies
pip install -r requirements.txt

# Generate coverage report
pytest --cov=app --cov-report=xml tests/

# For macOS/Linux users, install sonar-scanner
brew install sonar-scanner

# Or use Docker
docker run --rm \
  -e SONAR_HOST_URL="http://host.docker.internal:9000" \
  -e SONAR_TOKEN="<token>" \
  -v "$(pwd):/usr/src" \
  sonarsource/sonar-scanner-cli
```

#### Using the Helper Script

```bash
# Setup and start SonarQube
./scripts/sonarqube.sh setup

# Export your token
export SONAR_TOKEN=<your-token>

# Run analysis
./scripts/sonarqube.sh analyze

# View dashboard
./scripts/sonarqube.sh dashboard

# Stop when done
./scripts/sonarqube.sh stop
```

### Dashboard Review

After analysis completes:

1. Open http://localhost:9000 (local) or your SonarQube URL
2. View Project Dashboard:
   - **Overview**: Overall metrics
   - **Issues**: Bugs, Vulnerabilities, Code Smells
   - **Measures**: Detailed metrics
   - **Activity**: Analysis history
   - **Security Hotspots**: Security-critical code

### Key Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| **Reliability** | Bug potential | Grade A |
| **Security** | Vulnerability potential | Grade A |
| **Maintainability** | Technical debt | Grade A |
| **Coverage** | Code test coverage | 80%+ |
| **Duplicates** | Code duplication | <3% |
| **Hotspots** | Security-sensitive code reviewed | 100% |

---

## Code Issues and Remediation

### Common Issue Types

#### Bugs 🐛
- Logic errors
- Null pointer exceptions
- Type mismatches
- **Action**: Fix immediately

#### Vulnerabilities 🔓
- Security risks
- SQL injection potential
- Authentication issues
- **Action**: Fix before deployment

#### Code Smells 👃
- Poor coding practices
- Complex methods
- Unused imports
- Duplicate code
- **Action**: Refactor for maintainability

#### Security Hotspots 🔐
- Cryptography usage
- Authentication/Authorization
- Sensitive data handling
- **Action**: Review and confirm safe usage

---

## Bonus Task: SonarLint IDE Integration

### Install SonarLint

1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search for "SonarLint"
4. Install by SonarSource

### Configure Connection

1. Open Command Palette (Ctrl+Shift+P)
2. Type "Connect to SonarQube"
3. Enter SonarQube URL: http://localhost:9000
4. Enter token from SonarQube
5. Login and confirm

### Usage

- Issues appear in VS Code as you type
- Red squiggles indicate problems
- Hover for explanations
- Click "Fix" for automatic corrections when available
- Review suggestions in Problems panel

---

## Troubleshooting

### SonarQube Won't Start

```bash
# Check Docker logs
docker-compose -f docker-compose.sonarqube.yml logs sonarqube

# Increase memory (if needed)
docker update --memory 2g sonarqube-server

# Reset and start fresh
docker-compose -f docker-compose.sonarqube.yml down -v
docker-compose -f docker-compose.sonarqube.yml up -d
```

### Analysis Fails

```bash
# Verify token is set
echo $SONAR_TOKEN

# Test SonarQube connection
curl -u "$SONAR_TOKEN:" http://localhost:9000/api/system/status

# Check coverage.xml exists
ls -la coverage.xml
```

### Quality Gate Fails in CI/CD

1. Check SonarQube console for what failed
2. View Project Dashboard → Quality Gate tab
3. Identify failing conditions
4. Fix issues and push new commit

### No Coverage Report

```bash
# Ensure pytest-cov is installed
pip install pytest-cov

# Run tests with coverage
pytest --cov=app --cov-report=xml --cov-report=term-missing tests/

# Verify coverage.xml was created
cat coverage.xml | head -20
```

---

## Performance Tips

### Optimize Analysis

```properties
# In sonar-project.properties
sonar.qualitygate.wait=true
sonar.qualitygate.timeout=300
sonar.python.coverage.forceZeroCoverage=true
```

### Reduce Build Time

- Cache coverage reports
- Use incremental analysis
- Exclude test files from main analysis

---

## References

- [SonarQube Official Docs](https://docs.sonarqube.org/)
- [SonarQube Python Plugin](https://github.com/SonarSource/sonar-python)
- [Quality Gates Documentation](https://docs.sonarqube.org/latest/user-guide/quality-gates/)
- [Clean as You Code](https://docs.sonarqube.org/latest/user-guide/clean-as-you-code/)

---

## Support

For issues or questions:
1. Check SonarQube logs: `docker-compose -f docker-compose.sonarqube.yml logs sonarqube`
2. Review analysis results in SonarQube web UI
3. Check GitHub Actions workflow logs for CI/CD issues
4. Consult SonarQube documentation

---

**Last Updated**: March 5, 2026
**Version**: 1.0.0
