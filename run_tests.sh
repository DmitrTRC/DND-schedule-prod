#!/bin/bash

# Script to run tests and save results
# Author: DmitrTRC

cd /Users/dmitrymorozov/PycharmProjects/DND-schedule-prod

echo "=================================="
echo "Running ALL tests for Schedule DND"
echo "=================================="
echo ""

# Activate poetry environment and run tests
poetry run pytest -v --tb=short 2>&1 | tee logs/test_results.log

echo ""
echo "=================================="
echo "Test results saved to: logs/test_results.log"
echo "=================================="
