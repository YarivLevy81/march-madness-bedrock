#!/usr/bin/env python3
"""
Test script for the StatsRetriever class.
This script tests the ability to load team statistics from JSON files.
"""

import os
import json
import argparse
from dotenv import load_dotenv
from src.utils.stats_retriever import StatsRetriever

def test_stats_retriever(use_cache=True, verbose=False):
    """
    Test the StatsRetriever class.
    
    Args:
        use_cache (bool): Whether to use cached data
        verbose (bool): Whether to print verbose output
    """
    print("Testing StatsRetriever...")
    
    # Load environment variables
    load_dotenv()
    
    # Initialize stats retriever
    stats_retriever = StatsRetriever(
        year=2025,
        use_cache=use_cache
    )
    
    # Test team statistics
    print("\nTesting team statistics...")
    test_teams = ["Gonzaga", "Duke", "Kentucky", "North Carolina", "Kansas"]
    
    for team_name in test_teams:
        print(f"\nStatistics for {team_name}:")
        stats = stats_retriever.get_team_stats(team_name)
        
        if verbose:
            print(json.dumps(stats, indent=2))
        else:
            # Print a summary
            print(f"  Games played: {stats.get('gp', 'N/A')}")
            print(f"  Points: {stats.get('pts', 'N/A')}")
            print(f"  Field goal percentage: {stats.get('fgpct', 'N/A')}")
            print(f"  3-point percentage: {stats.get('3ppct', 'N/A')}")
            print(f"  Seed: {stats.get('seed', 'N/A')}")
            print(f"  Region: {stats.get('region', 'N/A')}")
    
    # Test team information
    print("\nTesting team information...")
    
    for team_name in test_teams:
        print(f"\nInformation for {team_name}:")
        info = stats_retriever.get_team_info(team_name)
        
        if verbose:
            print(json.dumps(info, indent=2))
        else:
            # Print a summary
            print(f"  Name: {info.get('name', 'N/A')}")
            print(f"  Seed: {info.get('seed', 'N/A')}")
            print(f"  Region: {info.get('region', 'N/A')}")
    
    print("\nTest complete!")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test the StatsRetriever class.")
    parser.add_argument("--no-cache", action="store_true", help="Don't use cached data")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print verbose output")
    
    args = parser.parse_args()
    
    test_stats_retriever(use_cache=not args.no_cache, verbose=args.verbose)

if __name__ == "__main__":
    main()
