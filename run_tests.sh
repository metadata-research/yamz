#!/bin/bash

# Colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to display usage information
show_help() {
    echo -e "${YELLOW}YAMZ Testing Script${NC}"
    echo "Usage: ./run_tests.sh [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help               Show this help message"
    echo "  -i, --install            Install testing dependencies"
    echo "  -u, --unittest           Run only unittest-based tests"
    echo "  -p, --pytest             Run only pytest-based tests"
    echo "  -c, --coverage           Generate coverage report"
    echo "  -v, --verbose            Run with verbose output"
    echo ""
    echo "Examples:"
    echo "  ./run_tests.sh           Run all tests"
    echo "  ./run_tests.sh -i -c     Install dependencies and run tests with coverage"
    echo "  ./run_tests.sh -p -v     Run only pytest tests with verbose output"
}

install_dependencies() {
    echo -e "${YELLOW}Installing test dependencies...${NC}"
    pip install -r requirements.txt
    echo -e "${GREEN}Dependencies installed successfully.${NC}"
}

run_unittest() {
    echo -e "${YELLOW}Running unittest tests...${NC}"
    if [ "$VERBOSE" = true ]; then
        python -m unittest discover -s app/tests -p "tests.py" -v
        python -m unittest discover -s app/tests -p "test_routes.py" -v
    else
        python -m unittest discover -s app/tests -p "tests.py"
        python -m unittest discover -s app/tests -p "test_routes.py"
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Unittest tests completed successfully.${NC}"
    else
        echo -e "${RED}Unittest tests failed.${NC}"
        exit 1
    fi
}

run_pytest() {
    echo -e "${YELLOW}Running pytest tests...${NC}"
    if [ "$COVERAGE" = true ]; then
        if [ "$VERBOSE" = true ]; then
            python -m pytest app/tests/test_pytest_*.py -v --cov=app --cov-report=term --cov-report=html
        else
            python -m pytest app/tests/test_pytest_*.py --cov=app --cov-report=term --cov-report=html
        fi
    else
        if [ "$VERBOSE" = true ]; then
            python -m pytest app/tests/test_pytest_*.py -v
        else
            python -m pytest app/tests/test_pytest_*.py
        fi
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Pytest tests completed successfully.${NC}"
        if [ "$COVERAGE" = true ]; then
            echo -e "${GREEN}Coverage report generated in htmlcov/ directory.${NC}"
        fi
    else
        echo -e "${RED}Pytest tests failed.${NC}"
        exit 1
    fi
}

# Default values
INSTALL=false
RUN_UNITTEST=true
RUN_PYTEST=true
COVERAGE=false
VERBOSE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -i|--install)
            INSTALL=true
            shift
            ;;
        -u|--unittest)
            RUN_UNITTEST=true
            RUN_PYTEST=false
            shift
            ;;
        -p|--pytest)
            RUN_UNITTEST=false
            RUN_PYTEST=true
            shift
            ;;
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Install dependencies if requested
if [ "$INSTALL" = true ]; then
    install_dependencies
fi

# Run the tests
if [ "$RUN_UNITTEST" = true ]; then
    run_unittest
fi

if [ "$RUN_PYTEST" = true ]; then
    run_pytest
fi

echo -e "${GREEN}All tests completed successfully!${NC}"
exit 0
