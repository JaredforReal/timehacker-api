#!/bin/bash

# 代码质量检查脚本
echo "🔍 Running Code Quality Checks..."

echo "1. Running Black (code formatting)..."
black --check app tests || {
    echo "❌ Black formatting issues found. Run 'black app tests' to fix."
    exit 1
}

echo "2. Running isort (import sorting)..."
isort --check-only app tests || {
    echo "❌ Import sorting issues found. Run 'isort app tests' to fix."
    exit 1
}

echo "3. Running Ruff (linting)..."
ruff check app tests || {
    echo "❌ Ruff linting issues found. Run 'ruff check --fix app tests' to fix."
    exit 1
}

echo "4. Running Flake8 (additional linting)..."
flake8 app tests || {
    echo "❌ Flake8 issues found."
    exit 1
}

echo "5. Running MyPy (type checking)..."
mypy app || {
    echo "❌ MyPy type checking issues found."
    exit 1
}

echo "6. Running Bandit (security checks)..."
bandit -r app -f json -o bandit-report.json || {
    echo "❌ Security issues found. Check bandit-report.json"
    exit 1
}

echo "✅ All code quality checks passed!"

echo "7. Running tests with coverage..."
pytest tests/ --cov=app --cov-report=html --cov-report=term

echo "📊 Coverage report generated in htmlcov/index.html"
