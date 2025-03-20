#!/usr/bin/env python3
"""
Test script to verify the NCAA March Madness Bracket Generator setup.
"""

import os
import sys
import importlib
import json
from dotenv import load_dotenv

def check_dependencies():
    """
    Check if all required dependencies are installed.
    
    Returns:
        bool: True if all dependencies are installed, False otherwise
    """
    print("Checking dependencies...")
    
    required_packages = [
        "boto3",
        "pandas",
        "requests",
        "dotenv",
        "tqdm",
        "tabulate"
    ]
    
    all_installed = True
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"  ✓ {package}")
        except ImportError as e:
            print(f"  ✗ {package} - Not installed: {e}")
            all_installed = False
    
    return all_installed

def check_aws_credentials():
    """
    Check if AWS credentials are configured.
    
    Returns:
        bool: True if AWS credentials are configured, False otherwise
    """
    print("\nChecking AWS credentials...")
    
    # Load environment variables
    load_dotenv()
    
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_region = os.getenv("AWS_REGION")
    
    if aws_access_key and aws_secret_key:
        print(f"  ✓ AWS credentials found")
        print(f"  ✓ AWS region: {aws_region or 'us-east-1 (default)'}")
        return True
    else:
        print("  ✗ AWS credentials not found")
        print("    Please create a .env file with your AWS credentials:")
        print("    AWS_ACCESS_KEY_ID=your_access_key_here")
        print("    AWS_SECRET_ACCESS_KEY=your_secret_key_here")
        print("    AWS_REGION=us-east-1")
        return False

def check_project_structure():
    """
    Check if the project structure is correct.
    
    Returns:
        bool: True if the project structure is correct, False otherwise
    """
    print("\nChecking project structure...")
    
    required_files = [
        "main.py",
        "requirements.txt",
        ".env.template",
        "README.md",
        "src/models/bedrock_client.py",
        "src/models/agent.py",
        "src/utils/bracket.py",
        "src/utils/stats_retriever.py"
    ]
    
    required_dirs = [
        "src",
        "src/models",
        "src/utils",
        "src/data",
        "results"
    ]
    
    all_exist = True
    
    for directory in required_dirs:
        if os.path.exists(directory) and os.path.isdir(directory):
            print(f"  ✓ {directory}/")
        else:
            print(f"  ✗ {directory}/ - Directory not found")
            all_exist = False
    
    for file_path in required_files:
        if os.path.exists(file_path) and os.path.isfile(file_path):
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} - File not found")
            all_exist = False
    
    return all_exist

def check_sample_data():
    """
    Check if sample data is available.
    
    Returns:
        bool: True if sample data is available, False otherwise
    """
    print("\nChecking sample data...")
    
    year = 2025
    data_files = [
        f"src/data/teams_{year}.json",
        f"src/data/team_stats_{year}.json",
        f"src/data/bracket_{year}.json"
    ]
    
    all_exist = True
    
    for file_path in data_files:
        if os.path.exists(file_path) and os.path.isfile(file_path):
            # Check if the file is valid JSON
            try:
                with open(file_path, "r") as f:
                    json.load(f)
                print(f"  ✓ {file_path}")
            except json.JSONDecodeError:
                print(f"  ✗ {file_path} - Invalid JSON")
                all_exist = False
        else:
            print(f"  ✗ {file_path} - File not found")
            all_exist = False
    
    if not all_exist:
        print("    You can generate sample data by running: python init_sample_data.py")
    
    return all_exist

def main():
    """Main function."""
    print("NCAA March Madness Bracket Generator - Setup Test")
    print("=" * 50)
    
    # Check dependencies
    deps_ok = check_dependencies()
    
    # Check AWS credentials
    aws_ok = check_aws_credentials()
    
    # Check project structure
    structure_ok = check_project_structure()
    
    # Check sample data
    data_ok = check_sample_data()
    
    # Print summary
    print("\nTest Summary:")
    print(f"  Dependencies: {'✓' if deps_ok else '✗'}")
    print(f"  AWS Credentials: {'✓' if aws_ok else '✗'}")
    print(f"  Project Structure: {'✓' if structure_ok else '✗'}")
    print(f"  Sample Data: {'✓' if data_ok else '✗'}")
    
    if deps_ok and aws_ok and structure_ok and data_ok:
        print("\n✅ All tests passed! You're ready to generate brackets.")
        print("\nNext steps:")
        print("1. Run the generator: python main.py")
        print("2. Visualize results: python visualize_results.py")
        print("3. Compare models: python compare_models.py")
        return 0
    else:
        print("\n❌ Some tests failed. Please fix the issues above before running the generator.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
