#!/usr/bin/env python3
"""
Visualization script for NCAA March Madness bracket results.
This script generates a text-based visualization of the bracket results.
"""

import os
import json
import argparse
from datetime import datetime

def load_results(filename):
    """
    Load results from a JSON file.
    
    Args:
        filename (str): Path to the results file
        
    Returns:
        dict: Loaded results
    """
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading results: {e}")
        return None

def print_bracket(results):
    """
    Print a text-based visualization of the bracket.
    
    Args:
        results (dict): Bracket results
    """
    if not results:
        print("No results to display.")
        return
    
    # Extract bracket data
    bracket_data = results.get("bracket", {})
    if not bracket_data:
        print("No bracket data found in results.")
        return
    
    # Print header
    print("\n" + "=" * 80)
    print(f"NCAA March Madness {bracket_data.get('year', 'Unknown Year')} Bracket")
    print("=" * 80)
    
    # Print champion
    champion = results.get("champion", "Unknown")
    print(f"\nChampion: {champion}")
    
    # Print Final Four
    final_four = results.get("final_four", [])
    print("\nFinal Four:")
    for team in final_four:
        print(f"  - {team}")
    
    # Print rounds
    rounds = bracket_data.get("results", {}).get("rounds", {})
    
    print("\nBracket Results:")
    print("-" * 80)
    
    # Print championship game
    if "6" in rounds and rounds["6"]:
        championship = rounds["6"][0]
        team1 = championship.get("team1", {}).get("name", "Unknown")
        team2 = championship.get("team2", {}).get("name", "Unknown")
        winner = championship.get("winner", {}).get("name", "Unknown")
        print(f"\nChampionship: {team1} vs {team2} -> {winner}")
        print(f"Reasoning: {championship.get('reasoning', 'No reasoning provided')[:200]}...")
    
    # Print Final Four
    if "5" in rounds and rounds["5"]:
        print("\nFinal Four:")
        for semifinal in rounds["5"]:
            team1 = semifinal.get("team1", {}).get("name", "Unknown")
            team2 = semifinal.get("team2", {}).get("name", "Unknown")
            winner = semifinal.get("winner", {}).get("name", "Unknown")
            print(f"  {team1} vs {team2} -> {winner}")
    
    # Print Elite 8
    if "4" in rounds and rounds["4"]:
        print("\nElite 8:")
        for matchup in rounds["4"]:
            team1 = matchup.get("team1", {}).get("name", "Unknown")
            team2 = matchup.get("team2", {}).get("name", "Unknown")
            winner = matchup.get("winner", {}).get("name", "Unknown")
            region = matchup.get("region", "Unknown")
            print(f"  {region}: {team1} vs {team2} -> {winner}")
    
    print("\n" + "=" * 80)

def list_result_files():
    """
    List all result files in the results directory.
    
    Returns:
        list: List of result files
    """
    results_dir = "results"
    if not os.path.exists(results_dir):
        print(f"Results directory '{results_dir}' not found.")
        return []
    
    result_files = []
    for filename in os.listdir(results_dir):
        if filename.endswith(".json"):
            result_files.append(os.path.join(results_dir, filename))
    
    return sorted(result_files)

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Visualize NCAA March Madness bracket results.")
    parser.add_argument("--file", "-f", help="Path to the results file")
    parser.add_argument("--list", "-l", action="store_true", help="List available result files")
    parser.add_argument("--all", "-a", action="store_true", help="Visualize all result files")
    
    args = parser.parse_args()
    
    if args.list:
        print("Available result files:")
        for filename in list_result_files():
            print(f"  {filename}")
        return
    
    if args.all:
        result_files = list_result_files()
        if not result_files:
            print("No result files found.")
            return
        
        for filename in result_files:
            results = load_results(filename)
            if results:
                print(f"\nResults from {filename}:")
                print_bracket(results)
        return
    
    if args.file:
        filename = args.file
        if not os.path.exists(filename):
            print(f"File '{filename}' not found.")
            return
    else:
        # Use the most recent result file
        result_files = list_result_files()
        if not result_files:
            print("No result files found. Run the generator first.")
            return
        
        filename = result_files[-1]
        print(f"Using most recent result file: {filename}")
    
    results = load_results(filename)
    if results:
        print_bracket(results)

if __name__ == "__main__":
    main()
