#!/usr/bin/env python3
"""
Setup script for NCAA March Madness Bracket Generator.
This script creates the necessary directories and initializes the .env file.
"""

import os
import shutil
import sys

def setup():
    """Set up the project by creating directories and initializing files."""
    print("Setting up NCAA March Madness Bracket Generator...")
    
    # Create directories
    directories = [
        "src/data",
        "results"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")
    
    # Create .env file from template if it doesn't exist
    if not os.path.exists(".env") and os.path.exists(".env.template"):
        shutil.copy(".env.template", ".env")
        print("Created .env file from template. Please edit it with your AWS credentials.")
    
    print("\nSetup complete!")
    print("\nNext steps:")
    print("1. Edit the .env file with your AWS credentials")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Run the generator: python main.py")

if __name__ == "__main__":
    setup()
