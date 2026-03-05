# 🪟 Windows Quick Start Guide - SonarQube Integration

## Assignment 03: SonarQube Setup for Windows Users

### ⚡ Quick Setup (5 minutes)

#### Step 1: Verify Prerequisites ✓

Open PowerShell and run:

```powershell
# Check Docker
docker --version

# Check Docker Compose
docker-compose --version

# Check Python
python --version  # Should be 3.13+
```

#### Step 2: Start SonarQube 🚀

```powershell
# Navigate to project
cd "C:\Users\<YourUsername>\Documents\GiangVH19_Final Exam Fast API"

# Start SonarQube (option 1 - Python script)
python scripts/sonarqube_helper.py setup

# OR (option 2 - Direct Docker)
docker-compose -f docker-compose.sonarqube.yml up -d
```

**Wait for output:**
```
✓ SonarQube is healthy
✓ SonarQube Dashboard Information:
  URL: http://localhost:9000
  Default Username: admin
  Default Password: admin (change on first login)
```

#### Step 3: Access SonarQube 🌐

1. Open browser: `http://localhost:9000`
2. Login credentials:
   - Username: `admin`
   - Password: `admin` (then change it!)

#### Step 4: Create Project & Token 🔑

**In SonarQube Web UI:**

1. Click "Create Project" → "Manually"
2. Project Key: `product-catalog-service`
3. Project Name: `Product Catalog Service`
4. Click "Set Up"
5. Select "Globally managed" → "Continue"
6. Copy the token (you'll need this)

**OR Use Auto-detection:**
1. Click "Create Project" → "Use existing configuration"
2. Select auto-detected project

#### Step 5: Set Environment Variable 🔐

**PowerShell:**
```powershell
$env:SONAR_TOKEN = "<your-token-here>"

# Verify it's set
echo $env:SONAR_TOKEN
```

**Command Prompt (CMD):**
```cmd
set SONAR_TOKEN=<your-token-here>

# Verify
echo %SONAR_TOKEN%
```

#### Step 6: Run Analysis 📊

```powershell
# This will:
# 1. Generate coverage report
# 2. Run SonarQube analysis
# 3. Show results in dashboard
python scripts/sonarqube_helper.py analyze
```

#### Step 7: Check Results 📈

Open dashboard: `http://localhost:9000/dashboard`

Look for:
- ✓ Coverage: 80%+
- ✓ Code Smells: As few as possible
- ✓ Bugs: 0
- ✓ Vulnerabilities: 0

---

## 🛠️ Helper Script Usage

### Available Commands

```powershell
# Start SonarQube and show info
python scripts/sonarqube_helper.py setup

# Stop SonarQube
python scripts/sonarqube_helper.py stop

# Restart SonarQube
python scripts/sonarqube_helper.py restart

# Generate coverage report only
python scripts/sonarqube_helper.py coverage

# Run full analysis (coverage + scan)
python scripts/sonarqube_helper.py analyze

# Show dashboard URL
python scripts/sonarqube_helper.py dashboard

# Show SonarQube logs
python scripts/sonarqube_helper.py logs
```

---

## 🐍 Common Tasks

### Run Tests Locally

```powershell
# Install dependencies first
pip install -r requirements.txt

# Run tests with coverage
pytest --cov=app --cov-report=xml --cov-report=term-missing tests/

# Check coverage percentage
type coverage.xml
```

### View Coverage Report

```powershell
# HTML report (opens in browser)
pytest --cov=app --cov-report=html tests/
.\htmlcov\index.html

# Or view in terminal
pytest --cov=app --cov-report=term-missing tests/
```

### Check SonarQube Health

```powershell
# Via Python script
python scripts/sonarqube_helper.py dashboard

# Via curl
curl http://localhost:9000/api/system/health

# Via PowerShell
Invoke-WebRequest -Uri "http://localhost:9000/api/system/health" | ConvertFrom-Json
```

---

## 🐛 Troubleshooting Windows-Specific Issues

### Issue: Port 9000 Already in Use

```powershell
# Find what's using port 9000
netstat -ano | findstr :9000

# If SonarQube is still running from before
docker-compose -f docker-compose.sonarqube.yml down

# Wait 10 seconds, then start again
Start-Sleep -Seconds 10
docker-compose -f docker-compose.sonarqube.yml up -d
```

### Issue: Docker Not Found

```powershell
# Check if Docker Desktop is running
Get-Service Docker

# Start Docker if not running
Start-Service Docker

# Or open Docker Desktop app manually
```

### Issue: Python Not Found

```powershell
# Use full path to Python from your venv
& ".\\.venv\Scripts\python.exe" scripts/sonarqube_helper.py setup

# Or if using system Python
python -c "import sys; print(sys.version)"
```

### Issue: Token Not Working

```powershell
# Verify token is set
echo $env:SONAR_TOKEN

# Re-export if empty
$env:SONAR_TOKEN = "squ_<your-new-token>"

# Test the token
$headers = @{"Authorization" = "Bearer $env:SONAR_TOKEN"}
Invoke-WebRequest -Uri "http://localhost:9000/api/user" -Headers $headers
```

### Issue: Analysis Takes Too Long

```powershell
# Check SonarQube logs
docker-compose -f docker-compose.sonarqube.yml logs sonarqube

# Increase Docker memory
docker update --memory 3g sonarqube-server

# Restart
docker-compose -f docker-compose.sonarqube.yml restart sonarqube
```

---

## 📋 Daily Workflow

### Morning Check

```powershell
# Ensure everything is running
docker-compose -f docker-compose.sonarqube.yml ps

# View project dashboard
start http://localhost:9000/dashboard
```

### Make Code Changes

```powershell
# Work on your code...
# (Make your changes in VS Code)
```

### Test Changes

```powershell
# Run tests and coverage
pytest --cov=app --cov-report=xml tests/

# Run SonarQube analysis
$env:SONAR_TOKEN = "<your-token>"
python scripts/sonarqube_helper.py analyze

# Check dashboard for any new issues
start http://localhost:9000/dashboard
```

### After Work

```powershell
# Optional: Stop SonarQube to free resources
docker-compose -f docker-compose.sonarqube.yml down

# Or keep it running (it will restart on reboot)
```

---

## 🔗 Important Links

| Resource | URL |
|----------|-----|
| **SonarQube Local Dashboard** | http://localhost:9000 |
| **Project Dashboard** | http://localhost:9000/dashboard |
| **Quality Gates** | http://localhost:9000/admin/qgates |
| **Account Settings** | http://localhost:9000/account/security |
| **Official Docs** | https://docs.sonarqube.org/ |

---

## 📚 Next Steps

1. ✅ Complete local setup
2. ✅ Run analysis locally
3. ✅ Review Quality Gate configuration
4. 🔄 Fix any code issues found
5. 🔄 Set up GitHub Actions secrets (for CI/CD)
6. 🔄 Push to GitHub and monitor pipeline

---

## 🆘 Need Help?

### Check These Files

- **Setup Guide**: `SONARQUBE_SETUP.md`
- **Full Report**: `ASSIGNMENT_03_REPORT.md`
- **Configuration**: `sonar-project.properties`
- **Docker Config**: `docker-compose.sonarqube.yml`

### View Logs

```powershell
# See what's happening in SonarQube
docker-compose -f docker-compose.sonarqube.yml logs -f sonarqube

# See database logs
docker-compose -f docker-compose.sonarqube.yml logs -f sonarqube-db

# Exit logs: Ctrl+C
```

### Reset Everything

```powershell
# If something goes wrong, fully reset
docker-compose -f docker-compose.sonarqube.yml down -v
docker volume rm docker_sonarqube_data docker_sonarqube_db_data

# Start fresh
python scripts/sonarqube_helper.py setup
```

---

## ✨ Pro Tips

1. **Keep SonarQube Running**: Leave it running in background while developing
2. **Use SonarLint**: Install extension for real-time feedback in VS Code
3. **Review Regularly**: Check dashboard after each major change
4. **Set Reminders**: Run analysis at least once per day
5. **Document Issues**: Create GitHub issues for any critical findings

---

**Last Updated**: March 5, 2026  
**Version**: 1.0 (Windows Edition)  
**Status**: ✅ Ready to Deploy

---

*For Linux/macOS users, consult the main `SONARQUBE_SETUP.md` guide.*
