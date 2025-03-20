#!/usr/bin/env python3
"""
Comparison script for NCAA March Madness bracket results from different models.
This script compares the predictions made by different models.
"""

import os
import json
import argparse
from datetime import datetime
from tabulate import tabulate

def load_all_results():
    """
    Load all result files from the results directory.
    
    Returns:
        dict: Dictionary of model name to results
    """
    results_dir = "results"
    if not os.path.exists(results_dir):
        print(f"Results directory '{results_dir}' not found.")
        return {}
    
    all_results = {}
    
    # Find the combined results file first
    combined_files = [f for f in os.listdir(results_dir) if f.startswith("all_results_")]
    if combined_files:
        # Use the most recent combined file
        combined_file = sorted(combined_files)[-1]
        combined_path = os.path.join(results_dir, combined_file)
        
        try:
            with open(combined_path, "r") as f:
                all_results = json.load(f)
                print(f"Loaded combined results from {combined_path}")
                return all_results
        except Exception as e:
            print(f"Error loading combined results: {e}")
    
    # If no combined file or error, load individual files
    for filename in os.listdir(results_dir):
        if filename.endswith(".json") and not filename.startswith("all_results_"):
            # Extract model name from filename
            model_name = filename.split("_")[0].replace("_", " ").title()
            
            try:
                with open(os.path.join(results_dir, filename), "r") as f:
                    results = json.load(f)
                    all_results[model_name] = results
                    print(f"Loaded results for {model_name}")
            except Exception as e:
                print(f"Error loading {filename}: {e}")
    
    return all_results

def compare_models(all_results):
    """
    Compare the predictions made by different models.
    
    Args:
        all_results (dict): Dictionary of model name to results
    """
    if not all_results:
        print("No results to compare.")
        return
    
    # Prepare comparison data
    comparison_data = []
    
    for model_name, results in all_results.items():
        champion = results.get("champion", "Unknown")
        final_four = results.get("final_four", [])
        time_taken = results.get("time_taken", 0)
        
        # Count unique regions in Final Four
        regions = set()
        if isinstance(results.get("bracket"), dict):
            for region_name in ["East", "West", "South", "Midwest"]:
                # Find the Elite 8 result for this region
                rounds = results["bracket"].get("results", {}).get("rounds", {})
                if "4" in rounds:
                    for result in rounds["4"]:
                        if result.get("region") == region_name and result.get("winner", {}).get("name") in final_four:
                            regions.add(region_name)
        
        # Get upset count (lower seed beating higher seed)
        upset_count = 0
        if isinstance(results.get("bracket"), dict):
            rounds = results["bracket"].get("results", {}).get("rounds", {})
            for round_key, matchups in rounds.items():
                for matchup in matchups:
                    team1 = matchup.get("team1", {})
                    team2 = matchup.get("team2", {})
                    winner = matchup.get("winner", {})
                    
                    # Check if this is an upset
                    if (team1.get("seed") and team2.get("seed") and winner.get("seed")):
                        if (team1.get("seed") < team2.get("seed") and winner.get("name") == team2.get("name")) or \
                           (team2.get("seed") < team1.get("seed") and winner.get("name") == team1.get("name")):
                            upset_count += 1
        
        comparison_data.append([
            model_name,
            champion,
            ", ".join(final_four[:4]),  # Limit to 4 teams
            len(regions),
            upset_count,
            f"{time_taken:.2f}s" if time_taken else "N/A"
        ])
    
    # Print comparison table
    headers = ["Model", "Champion", "Final Four", "Regions", "Upsets", "Time"]
    print("\n" + tabulate(comparison_data, headers=headers, tablefmt="grid"))

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Compare NCAA March Madness bracket results from different models.")
    parser.add_argument("--detail", "-d", action="store_true", help="Show detailed comparison")
    
    args = parser.parse_args()
    
    print("Comparing model predictions for NCAA March Madness brackets...")
    all_results = load_all_results()
    
    if not all_results:
        print("No results found. Run the generator first.")
        return
    
    compare_models(all_results)
    
    if args.detail:
        print("\nDetailed Comparison:")
        print("=" * 80)
        
        # Get all models
        models = list(all_results.keys())
        
        # Compare Final Four picks
        print("\nFinal Four Picks:")
        for model in models:
            final_four = all_results[model].get("final_four", [])
            print(f"  {model}: {', '.join(final_four)}")
        
        # Compare Elite 8 picks
        print("\nElite 8 Picks:")
        for model in models:
            elite_8 = []
            if isinstance(all_results[model].get("bracket"), dict):
                rounds = all_results[model]["bracket"].get("results", {}).get("rounds", {})
                if "4" in rounds:
                    for result in rounds["4"]:
                        winner = result.get("winner", {}).get("name")
                        if winner:
                            elite_8.append(winner)
            
            print(f"  {model}: {', '.join(elite_8)}")
        
        # Compare reasoning for championship pick
        print("\nChampionship Reasoning:")
        for model in models:
            if isinstance(all_results[model].get("bracket"), dict):
                rounds = all_results[model]["bracket"].get("results", {}).get("rounds", {})
                if "6" in rounds and rounds["6"]:
                    championship = rounds["6"][0]
                    reasoning = championship.get("reasoning", "No reasoning provided")
                    print(f"\n  {model}:")
                    print(f"    {reasoning[:300]}...")

if __name__ == "__main__":
    main()
