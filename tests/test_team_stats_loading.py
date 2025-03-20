#!/usr/bin/env python3
"""
Test script to verify that the StatsRetriever is correctly loading team statistics
from individual JSON files in the team_stats directory.
"""

from src.utils.stats_retriever import StatsRetriever
import json
import os

def main():
    # Initialize the stats retriever
    stats_retriever = StatsRetriever()
    
    # Get stats for a few teams
    test_teams = ["Gonzaga", "Duke", "Kentucky", "UConn", "Houston"]
    
    print("Testing team stats loading from individual JSON files:")
    print("-" * 50)
    
    for team_name in test_teams:
        print(f"\nStats for {team_name}:")
        team_stats = stats_retriever.get_team_stats(team_name)
        
        # Print some key stats
        if team_stats:
            print(f"  Games played: {team_stats.get('gp', 'N/A')}")
            print(f"  Points: {team_stats.get('pts', 'N/A')}")
            print(f"  Field goal percentage: {team_stats.get('fgpct', 'N/A')}")
            print(f"  3-point percentage: {team_stats.get('3ppct', 'N/A')}")
            print(f"  Seed: {team_stats.get('seed', 'N/A')}")
            print(f"  Region: {team_stats.get('region', 'N/A')}")
            
            # Print the source of the stats (to verify they're from JSON files)
            team_file = os.path.join("src/data/team_stats", f"{team_name}.json")
            if os.path.exists(team_file):
                print(f"  [Stats loaded from {team_file}]")
            else:
                print(f"  [Stats not loaded from file - file {team_file} does not exist]")
        else:
            print("  No stats found for this team")
    
    # Print the total number of teams with stats
    print("\n" + "-" * 50)
    print(f"Total teams with stats: {len(stats_retriever.team_stats)}")
    print("Team names with stats:")
    for i, team_name in enumerate(sorted(stats_retriever.team_stats.keys())):
        print(f"  {i+1}. {team_name}")

if __name__ == "__main__":
    main()
