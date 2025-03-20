#!/usr/bin/env python3
"""
Script to make Python files executable.
"""

import os
import stat
import sys

def make_executable(file_path):
    """
    Make a file executable.
    
    Args:
        file_path (str): Path to the file
    """
    # Get current permissions
    current_permissions = os.stat(file_path).st_mode
    
    # Add executable permissions
    os.chmod(file_path, current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    
    print(f"Made {file_path} executable")

def main():
    """Main function."""
    # List of files to make executable
    files = [
        "main.py",
        "setup.py",
        "visualize_results.py",
        "compare_models.py",
        "init_sample_data.py",
        "run_single_model.py",
        "make_executable.py",
        "test_stats_retriever.py",
        "test_setup.py",
        "generate_report.py"
    ]
    
    print("Making Python files executable...")
    
    for file_path in files:
        if os.path.exists(file_path):
            make_executable(file_path)
        else:
            print(f"Warning: {file_path} not found")
    
    print("\nDone!")
    print("\nYou can now run the scripts directly, e.g.:")
    print("  ./setup.py")
    print("  ./main.py")

if __name__ == "__main__":
    main()
