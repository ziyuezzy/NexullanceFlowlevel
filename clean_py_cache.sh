#!/bin/bash
# List and remove Python cache files after confirmation

# Find all cache directories and files
cache_dirs=$(find . -type d -name "__pycache__")
pyc_files=$(find . -type f -name "*.pyc")
pyo_files=$(find . -type f -name "*.pyo")
pyd_files=$(find . -type f -name "*.pyd")

# Show what will be deleted
echo "The following will be deleted:"
echo -e "\n__pycache__ directories:"
if [ -n "$cache_dirs" ]; then
    echo "$cache_dirs"
else
    echo "None found"
fi

echo -e "\n.pyc files:"
if [ -n "$pyc_files" ]; then
    echo "$pyc_files"
else
    echo "None found"
fi

echo -e "\n.pyo files:"
if [ -n "$pyo_files" ]; then
    echo "$pyo_files"
else
    echo "None found"
fi

echo -e "\n.pyd files:"
if [ -n "$pyd_files" ]; then
    echo "$pyd_files"
else
    echo "None found"
fi

# Ask for confirmation
read -p "Do you want to proceed with deletion? (y/N) " confirm

if [[ $confirm =~ ^[Yy]$ ]]; then
    find . -type d -name "__pycache__" -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete
    find . -type f -name "*.pyo" -delete
    find . -type f -name "*.pyd" -delete
    echo "Python cache cleaned."
else
    echo "Operation cancelled."
fi