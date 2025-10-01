#!/bin/bash
# Run tests for the new architecture

echo "🧪 Running tests for Sales Compensation Dashboard Engine..."
echo ""

cd "$(dirname "$0")"

# Set PYTHONPATH to include project root
export PYTHONPATH=$PWD:$PYTHONPATH

# Run tests
pytest modules/tests/test_engine.py -v --tb=short

echo ""
if [ $? -eq 0 ]; then
    echo "✅ All tests passed! Engine is working correctly."
else
    echo "❌ Some tests failed. Check the output above."
fi
