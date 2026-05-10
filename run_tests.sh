#!/bin/bash
# Run unit tests for deepArchive-OCR project

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Running Unit Tests${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${YELLOW}pytest not found. Installing dependencies...${NC}"
    pip install -q -r requirements-dev.txt
fi

# Run pytest with coverage
echo -e "\n${YELLOW}Running tests with coverage...${NC}"
pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html "$@"

# Check exit code
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}  All tests passed!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "\nCoverage report generated in htmlcov/"
else
    echo -e "\n${RED}========================================${NC}"
    echo -e "${RED}  Tests failed!${NC}"
    echo -e "${RED}========================================${NC}"
    exit 1
fi
