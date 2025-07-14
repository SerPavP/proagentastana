#!/bin/bash

# ProAgentAstana Deployment Script
# This script sets up the Django application for production deployment

echo "🚀 ProAgentAstana Deployment Script"
echo "=================================="

# Check if Python 3.11 is available
if ! command -v python &> /dev/null; then
    echo "❌ Python 3.11 is required but not installed."
    exit 1
fi

echo "✅ Python 3.11 found"

# Install required packages
echo "📦 Installing required packages..."
python -m pip install django psycopg2-binary python-decouple pillow

# Apply database migrations
echo "🗄️ Setting up database..."
python manage.py migrate

# Populate sample data
echo "📊 Populating sample data..."
python manage.py populate_sample_data

# Collect static files (for production)
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "✅ Deployment completed successfully!"
echo ""
echo "🌐 To start the development server:"
echo "   python manage.py runserver 0.0.0.0:8000"
echo ""
echo "🔑 Access Information:"
echo "   Application: http://localhost:8000/"
echo "   Admin Panel: http://localhost:8000/admin/"
echo "   Sample User: +77771234567 / testpass123"
echo "   Admin User:  +77777777777 / admin123"
echo ""
echo "📚 For more information, see README.md"

