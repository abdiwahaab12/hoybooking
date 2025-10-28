#!/bin/bash

echo "========================================"
echo "Resume/CV Website Setup Script"
echo "========================================"
echo

echo "Installing Python dependencies..."
pip3 install -r requirements.txt

echo
echo "Setting up database..."
python3 database_setup.py

echo
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo
echo "To start the website:"
echo "  python3 run.py"
echo
echo "Website: http://localhost:5000"
echo "Admin: http://localhost:5000/admin"
echo "Login: admin / admin123"
echo
