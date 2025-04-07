#!/bin/bash

# Default values
install_deps=false
run_unittest=true
run_pytest=true
coverage=false
verbose=false

# Parse command-line options
while getopts "iupcv" opt; do
  case $opt in
    i) install_deps=true ;;
    u) run_unittest=true; run_pytest=false ;;
    p) run_pytest=true; run_unittest=false ;;
    c) coverage=true ;;
    v) verbose=true ;;
    *) echo "Usage: $0 [-i] [-u] [-p] [-c] [-v]"; exit 1 ;;
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

# Run unittest tests if requested
if [ "$run_unittest" = true ]; then
  echo "Running unittest tests..."
  if [ "$verbose" = true ]; then
    python -m unittest discover -s app/tests -p "tests.py" -v
  else
    python -m unittest discover -s app/tests -p "tests.py"
  fi
  
  if [ $? -eq 0 ]; then
    echo "Unittest tests passed."
  else
    echo "Unittest tests failed."
  fi
fi

# Run pytest tests if requested
if [ "$run_pytest" = true ]; then
  echo "Running pytest tests..."
  
  if [ "$coverage" = true ]; then
    if [ "$verbose" = true ]; then
      python -m pytest app/tests/test_pytest*.py -v --cov=app --cov-report=html:test_output/coverage
    else
      python -m pytest app/tests/test_pytest*.py --cov=app --cov-report=html:test_output/coverage
    fi
  else
    if [ "$verbose" = true ]; then
      python -m pytest app/tests/test_pytest*.py -v
    else
      python -m pytest app/tests/test_pytest*.py
    fi
  fi
  
  if [ $? -eq 0 ]; then
    echo "Pytest tests passed."
    if [ "$coverage" = true ]; then
      echo "Coverage report generated in test_output/coverage/"
    fi
  else
    echo "Pytest tests failed."
  fi
fi

exit 0
