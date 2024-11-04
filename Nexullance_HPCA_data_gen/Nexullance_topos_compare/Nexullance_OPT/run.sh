#!/bin/bash

# Find all Python scripts in the current directory
python_scripts=$(find . -maxdepth 1 -type f -name "*.py")

# Iterate over each Python script and execute it
for script in $python_scripts; do
    echo "Executing script: $script"
    python3.12 $script
done
