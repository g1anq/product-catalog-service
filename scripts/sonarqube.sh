#!/bin/bash

# SonarQube Setup and Test Script
# This script helps set up SonarQube locally and run code analysis

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Product Catalog Service - SonarQube Setup ===${NC}\n"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed${NC}"
    exit 1
fi

# Function to start SonarQube
start_sonarqube() {
    echo -e "${BLUE}Starting SonarQube containers...${NC}"
    docker-compose -f docker-compose.sonarqube.yml up -d
    
    echo -e "${YELLOW}Waiting for SonarQube to be ready...${NC}"
    for i in {1..60}; do
        if curl -s http://localhost:9000/api/system/health | grep -q '"status":"UP"'; then
            echo -e "${GREEN}SonarQube is ready!${NC}"
            return 0
        fi
        echo "Attempt $i/60..."
        sleep 2
    done
    
    echo -e "${RED}SonarQube failed to start${NC}"
    return 1
}

# Function to stop SonarQube
stop_sonarqube() {
    echo -e "${BLUE}Stopping SonarQube containers...${NC}"
    docker-compose -f docker-compose.sonarqube.yml down
    echo -e "${GREEN}SonarQube stopped${NC}"
}

# Function to run analysis
run_analysis() {
    echo -e "${BLUE}Running code analysis...${NC}"
    
    # Check if sonar-scanner is installed
    if ! command -v sonar-scanner &> /dev/null; then
        echo -e "${YELLOW}sonar-scanner not found. Attempting to use Docker...${NC}"
        docker run --rm \
            -e SONAR_HOST_URL="http://host.docker.internal:9000" \
            -e SONAR_TOKEN="${SONAR_TOKEN}" \
            -v "$(pwd):/usr/src" \
            sonarsource/sonar-scanner-cli \
            -Dsonar.projectBaseDir=/usr/src \
            -Dsonar.python.coverage.reportPaths=/usr/src/coverage.xml
    else
        sonar-scanner \
            -Dsonar.projectBaseDir="$(pwd)" \
            -Dsonar.host.url="http://localhost:9000" \
            -Dsonar.token="${SONAR_TOKEN}"
    fi
    
    echo -e "${GREEN}Analysis complete!${NC}"
}

# Function to generate coverage report
generate_coverage() {
    echo -e "${BLUE}Generating coverage report...${NC}"
    python -m pytest --cov=app --cov-report=xml --cov-report=term-missing tests/
    echo -e "${GREEN}Coverage report generated${NC}"
}

# Function to show dashboard link
show_dashboard() {
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}SonarQube Dashboard: http://localhost:9000${NC}"
    echo -e "${GREEN}Default credentials:${NC}"
    echo -e "${GREEN}  Username: admin${NC}"
    echo -e "${GREEN}  Password: admin${NC}"
    echo -e "${GREEN}========================================${NC}"
}

# Main menu
case "${1:-help}" in
    start)
        start_sonarqube
        show_dashboard
        ;;
    stop)
        stop_sonarqube
        ;;
    analyze)
        if [ -z "${SONAR_TOKEN}" ]; then
            echo -e "${RED}Error: SONAR_TOKEN environment variable not set${NC}"
            echo -e "${YELLOW}Set it with: export SONAR_TOKEN=<your-token>${NC}"
            exit 1
        fi
        generate_coverage
        run_analysis
        ;;
    setup)
        start_sonarqube
        show_dashboard
        echo -e "\n${YELLOW}Next steps:${NC}"
        echo "1. Open http://localhost:9000"
        echo "2. Login with admin/admin"
        echo "3. Create a new project or use auto-detection"
        echo "4. Generate an authentication token in account settings"
        echo "5. Export token: export SONAR_TOKEN=<your-token>"
        echo "6. Run: ./scripts/sonarqube.sh analyze"
        ;;
    restart)
        stop_sonarqube
        start_sonarqube
        show_dashboard
        ;;
    dashboard)
        show_dashboard
        ;;
    logs)
        docker-compose -f docker-compose.sonarqube.yml logs -f sonarqube
        ;;
    *)
        echo -e "${BLUE}Usage: $0 {start|stop|restart|analyze|setup|dashboard|logs}${NC}\n"
        echo "Commands:"
        echo "  start     - Start SonarQube containers"
        echo "  stop      - Stop SonarQube containers"
        echo "  restart   - Restart SonarQube containers"
        echo "  setup     - Complete setup (start + show credentials)"
        echo "  analyze   - Run code analysis (requires SONAR_TOKEN env var)"
        echo "  dashboard - Show SonarQube dashboard URL"
        echo "  logs      - Show SonarQube container logs"
        echo ""
        echo -e "${YELLOW}Example workflow:${NC}"
        echo "  1. $0 setup"
        echo "  2. Configure your SonarQube project and generate token"
        echo "  3. export SONAR_TOKEN=<token>"
        echo "  4. $0 analyze"
        exit 0
        ;;
esac
