#!/bin/bash

# Default values
install_deps=false
run_tests=true
coverage=false
verbose=false

# Parse command-line options
while getopts "icv" opt; do
  case $opt in
    i) install_deps=true ;;
    c) coverage=true ;;
    v) verbose=true ;;
    *) echo "Usage: $0 [-i] [-c] [-v]"; exit 1 ;;
  esac
done

# Install dependencies if requested
if [ "$install_deps" = true ]; then
  echo "Installing test dependencies..."
  pip install -r requirements.txt
  if [ $? -eq 0 ]; then
    echo "Dependencies installed successfully."
  else
    echo "Failed to install dependencies."
    exit 1
  fi
fi

# Environment setup
export TESTING=True
export FLASK_ENV=testing
export SQLALCHEMY_DATABASE_URI=sqlite:///:memory:

# Create test output directory
mkdir -p test_output

# Run tests
if [ "$run_tests" = true ]; then
  echo "Running tests..."
  
  if [ "$coverage" = true ]; then
    if [ "$verbose" = true ]; then
      python -m pytest app/tests/test_basic.py -v --cov=app --cov-report=html:test_output/coverage
    else
      python -m pytest app/tests/test_basic.py --cov=app --cov-report=html:test_output/coverage
    fi
  else
    if [ "$verbose" = true ]; then
      python -m pytest app/tests/test_basic.py -v
    else
      python -m pytest app/tests/test_basic.py
    fi
  fi
  
  exit_code=$?
  
  if [ $exit_code -eq 0 ]; then
    echo "Tests passed successfully!"
    
    if [ "$coverage" = true ]; then
      echo "Coverage report generated in test_output/coverage/"
    fi
  else
    echo "Tests failed."
    exit $exit_code
  fi
fi

exit 0
