#!/bin/bash

# 代码自动修复脚本
echo "🔧 Auto-fixing code issues..."

echo "1. Running Black (auto-format)..."
black app tests

echo "2. Running isort (auto-sort imports)..."
isort app tests

echo "3. Running Ruff (auto-fix linting issues)..."
ruff check --fix app tests

echo "✅ Code auto-fixes completed!"
echo "💡 Run 'scripts/check_quality.sh' to verify all issues are resolved."
