#!/bin/bash

# Sales Compensation Dashboard Launcher
echo "🚀 Starting Sales Compensation & Monte Carlo Dashboard..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python3 first."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "streamlit_env" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv streamlit_env
fi

# Activate virtual environment and install requirements
echo "📦 Installing required packages in virtual environment..."
source streamlit_env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Run the dashboard
echo "🎯 Launching dashboard at http://localhost:8501"
echo "📊 Use Ctrl+C to stop the dashboard"
echo "🔗 Open your browser and navigate to: http://localhost:8501"
streamlit run sales_compensation_dashboard.py
