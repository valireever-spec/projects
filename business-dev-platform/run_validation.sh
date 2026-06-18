#!/bin/bash
# Complete validation test suite for Business Dev Platform

set -e

PROJECT_DIR="/home/vali/projects/business-dev-platform"
VENV_DIR="$PROJECT_DIR/venv"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Business Dev Platform - Validation Suite${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Activate virtual environment
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
    echo -e "${GREEN}✓ Virtual environment activated${NC}"
else
    echo -e "${RED}✗ Virtual environment not found${NC}"
    exit 1
fi

cd "$PROJECT_DIR"

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0

# Function to run test suite
run_test_suite() {
    local test_path=$1
    local test_name=$2

    echo ""
    echo -e "${BLUE}Running: $test_name${NC}"
    echo "Path: $test_path"
    echo "-------------------------------------------"

    if pytest "$test_path" -v --tb=short 2>&1 | tee /tmp/test_output.txt; then
        echo -e "${GREEN}✓ $test_name passed${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ $test_name failed${NC}"
        ((TESTS_FAILED++))
        cat /tmp/test_output.txt
    fi
}

# 1. Unit Tests - Domain Scorer
echo -e "${YELLOW}[1/6] Testing Domain Scoring Algorithm${NC}"
run_test_suite "tests/unit/test_domain_scorer.py" "Domain Scorer Tests"

# 2. Unit Tests - Financial Model
echo -e "${YELLOW}[2/6] Testing Financial Projection Model${NC}"
run_test_suite "tests/unit/test_financial_model.py" "Financial Model Tests"

# 3. Unit Tests - Risk Scorer
echo -e "${YELLOW}[3/6] Testing Risk Assessment Model${NC}"
run_test_suite "tests/unit/test_risk_scorer.py" "Risk Scorer Tests"

# 4. Integration Tests - Export
echo -e "${YELLOW}[4/6] Testing Export Functionality${NC}"
run_test_suite "tests/integration/test_export.py" "Export Tests"

# 5. System Validation - Full Workflow
echo -e "${YELLOW}[5/6] Testing Complete System Workflow${NC}"
run_test_suite "tests/integration/test_system_validation.py" "System Validation Tests"

# 6. Code Coverage Analysis
echo -e "${YELLOW}[6/6] Analyzing Code Coverage${NC}"
echo "-------------------------------------------"

if pytest tests/ --cov=backend --cov-report=term-missing --cov-report=html -q 2>&1 | tee /tmp/coverage.txt; then
    echo -e "${GREEN}✓ Code coverage analysis complete${NC}"
    COVERAGE=$(grep -oP 'TOTAL.*\K[0-9]+(?=%)' /tmp/coverage.txt | tail -1)
    echo -e "Coverage: ${COVERAGE}%"
else
    echo -e "${YELLOW}⚠ Coverage analysis skipped${NC}"
fi

# Summary
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}VALIDATION SUMMARY${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Passed:  $TESTS_PASSED${NC}"
echo -e "${RED}Failed:  $TESTS_FAILED${NC}"
echo -e "${YELLOW}Skipped: $TESTS_SKIPPED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All validation tests passed!${NC}"
    echo ""
    echo "The platform is ready for deployment with:"
    echo "  • 80+ unit and integration tests"
    echo "  • Complete algorithm validation"
    echo "  • Data plausibility checks"
    echo "  • End-to-end workflow verification"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Some tests failed. Review output above.${NC}"
    exit 1
fi
