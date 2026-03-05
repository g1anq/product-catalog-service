#!/usr/bin/env python3
"""
SonarQube Setup and Analysis Helper Script
Supports Windows, macOS, and Linux
"""

import subprocess
import sys
import time
import os
import json
import argparse
from pathlib import Path
from typing import Optional
import requests


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def disable():
        """Disable colors on Windows (if not supported)"""
        for attr in dir(Colors):
            if not attr.startswith('_'):
                setattr(Colors, attr, '')


# Detect if running on Windows and disable colors if needed
if sys.platform == 'win32':
    try:
        # Try to enable ANSI colors in Windows 10+
        os.system('color')
    except:
        Colors.disable()


def print_header(text: str):
    """Print formatted header"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")


def print_step(text: str):
    """Print a step message"""
    print(f"{Colors.CYAN}→ {text}{Colors.ENDC}")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.ENDC}")


def run_command(cmd: list, description: str = None) -> bool:
    """Run a shell command and return success status"""
    if description:
        print_step(description)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print_error(f"Command failed: {' '.join(cmd)}")
            if result.stderr:
                print(f"{Colors.RED}{result.stderr}{Colors.ENDC}")
            return False
        return True
    except Exception as e:
        print_error(f"Error running command: {e}")
        return False


def check_docker_installed() -> bool:
    """Check if Docker is installed"""
    try:
        subprocess.run(['docker', '--version'], capture_output=True, check=True)
        print_success("Docker is installed")
        return True
    except:
        print_error("Docker is not installed")
        return False


def check_docker_compose_installed() -> bool:
    """Check if Docker Compose is installed"""
    try:
        subprocess.run(['docker-compose', '--version'], capture_output=True, check=True)
        print_success("Docker Compose is installed")
        return True
    except:
        print_error("Docker Compose is not installed")
        return False


def check_sonarqube_health(host: str = "http://localhost:9000") -> bool:
    """Check if SonarQube is running and healthy"""
    try:
        response = requests.get(f"{host}/api/system/health", timeout=2)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'UP':
                print_success("SonarQube is healthy")
                return True
    except:
        pass
    return False


def wait_for_sonarqube(timeout: int = 120, host: str = "http://localhost:9000"):
    """Wait for SonarQube to be ready"""
    print_step("Waiting for SonarQube to be ready...")
    start = time.time()
    
    while time.time() - start < timeout:
        if check_sonarqube_health(host):
            return True
        
        elapsed = int(time.time() - start)
        remaining = timeout - elapsed
        print(f"  Waiting... ({elapsed}s/{timeout}s)", end='\r')
        time.sleep(3)
    
    print_error(f"SonarQube did not start within {timeout} seconds")
    return False


def start_sonarqube():
    """Start SonarQube containers"""
    print_header("Task 3.1: Starting SonarQube")
    
    if not check_docker_installed() or not check_docker_compose_installed():
        return False
    
    if check_sonarqube_health():
        print_warning("SonarQube is already running")
        return True
    
    if not run_command(
        ['docker-compose', '-f', 'docker-compose.sonarqube.yml', 'up', '-d'],
        "Starting SonarQube containers..."
    ):
        return False
    
    if not wait_for_sonarqube():
        return False
    
    print_success("SonarQube started successfully")
    show_dashboard_info()
    return True


def stop_sonarqube():
    """Stop SonarQube containers"""
    print_header("Stopping SonarQube")
    
    if not check_docker_installed() or not check_docker_compose_installed():
        return False
    
    if run_command(
        ['docker-compose', '-f', 'docker-compose.sonarqube.yml', 'down'],
        "Stopping SonarQube containers..."
    ):
        print_success("SonarQube stopped")
        return True
    
    return False


def restart_sonarqube():
    """Restart SonarQube containers"""
    print_header("Restarting SonarQube")
    
    if not stop_sonarqube():
        return False
    
    time.sleep(2)
    
    return start_sonarqube()


def generate_coverage():
    """Generate coverage report"""
    print_header("Task 3.2: Generating Coverage Report")
    
    print_step("Running tests with coverage...")
    cmd = [
        sys.executable, '-m', 'pytest',
        '--cov=app',
        '--cov-report=xml',
        '--cov-report=term-missing',
        'tests/'
    ]
    
    if not run_command(cmd, "Running pytest..."):
        return False
    
    coverage_file = Path('coverage.xml')
    if coverage_file.exists():
        print_success(f"Coverage report generated: {coverage_file}")
        return True
    else:
        print_error("Coverage report not found")
        return False


def run_sonarqube_analysis():
    """Run SonarQube analysis"""
    print_header("Task 3.2: Running SonarQube Analysis")
    
    sonar_token = os.getenv('SONAR_TOKEN')
    if not sonar_token:
        print_error("SONAR_TOKEN environment variable not set")
        print_warning("Set it with: export SONAR_TOKEN=<your-token>")
        return False
    
    # Try to use sonar-scanner directly
    try:
        cmd = [
            'sonar-scanner',
            '-Dsonar.projectBaseDir=.',
            '-Dsonar.host.url=http://localhost:9000',
            f'-Dsonar.token={sonar_token}'
        ]
        
        print_step("Running sonar-scanner...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print_success("Analysis completed successfully")
            return True
        else:
            print_warning("sonar-scanner returned non-zero exit code")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except FileNotFoundError:
        print_warning("sonar-scanner not found in PATH")
        print_step("Attempting to use Docker sonar-scanner...")
        
        # Fallback to Docker
        cwd = str(Path.cwd())
        cmd = [
            'docker', 'run', '--rm',
            '-e', f'SONAR_HOST_URL=http://host.docker.internal:9000',
            '-e', f'SONAR_TOKEN={sonar_token}',
            '-v', f'{cwd}:/usr/src',
            'sonarsource/sonar-scanner-cli',
            '-Dsonar.projectBaseDir=/usr/src',
            '-Dsonar.python.coverage.reportPaths=/usr/src/coverage.xml'
        ]
        
        return run_command(cmd, "Running sonar-scanner via Docker...")


def analyze():
    """Run complete analysis (coverage + SonarQube)"""
    print_header("Running Complete Analysis")
    
    if not generate_coverage():
        return False
    
    if not run_sonarqube_analysis():
        return False
    
    print_success("Analysis complete!")
    show_dashboard_info()
    return True


def show_dashboard_info():
    """Show SonarQube dashboard information"""
    print(f"\n{Colors.GREEN}{Colors.BOLD}SonarQube Dashboard Information:{Colors.ENDC}")
    print(f"  URL: {Colors.CYAN}http://localhost:9000{Colors.ENDC}")
    print(f"  Default Username: {Colors.CYAN}admin{Colors.ENDC}")
    print(f"  Default Password: {Colors.CYAN}admin{Colors.ENDC}")
    print()


def setup():
    """Complete setup (start + show info)"""
    if not start_sonarqube():
        return False
    
    print(f"\n{Colors.YELLOW}Next Steps:{Colors.ENDC}")
    print("1. Open http://localhost:9000")
    print("2. Login with admin/admin (change password on first login)")
    print("3. Create a new project or use auto-detection")
    print("4. Generate an authentication token in account settings")
    print("5. Export token: set SONAR_TOKEN=<your-token> (Windows)")
    print("   or: export SONAR_TOKEN=<your-token> (macOS/Linux)")
    print(f"6. Run: python scripts/sonarqube_helper.py analyze")
    return True


def show_logs():
    """Show SonarQube logs"""
    print_header("SonarQube Logs")
    
    cmd = ['docker-compose', '-f', 'docker-compose.sonarqube.yml', 'logs', '-f', 'sonarqube']
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print_warning("Log stream stopped")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='SonarQube Setup and Analysis Helper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/sonarqube_helper.py setup       # Start SonarQube and show info
  python scripts/sonarqube_helper.py analyze     # Run full analysis
  python scripts/sonarqube_helper.py start       # Start SonarQube
  python scripts/sonarqube_helper.py stop        # Stop SonarQube
        """
    )
    
    parser.add_argument(
        'command',
        choices=['start', 'stop', 'restart', 'analyze', 'setup', 'dashboard', 'logs', 'coverage'],
        help='Command to execute'
    )
    
    args = parser.parse_args()
    
    commands = {
        'start': start_sonarqube,
        'stop': stop_sonarqube,
        'restart': restart_sonarqube,
        'analyze': analyze,
        'setup': setup,
        'dashboard': show_dashboard_info,
        'logs': show_logs,
        'coverage': generate_coverage,
    }
    
    try:
        result = commands[args.command]()
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print_warning("\nOperation cancelled")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
