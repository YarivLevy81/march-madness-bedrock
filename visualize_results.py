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

def print_bracket(results, full_bracket=False):
    """
    Print a text-based visualization of the bracket.
    
    Args:
        results (dict): Bracket results
        full_bracket (bool): Whether to print the full bracket with all rounds
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
        team1_obj = championship.get("team1", {})
        team2_obj = championship.get("team2", {})
        winner_obj = championship.get("winner", {})
        
        team1_name = team1_obj.get("name", "Unknown") if isinstance(team1_obj, dict) else str(team1_obj)
        team2_name = team2_obj.get("name", "Unknown") if isinstance(team2_obj, dict) else str(team2_obj)
        winner_name = winner_obj.get("name", "Unknown") if isinstance(winner_obj, dict) else str(winner_obj)
        
        team1_seed = team1_obj.get("seed", "N/A") if isinstance(team1_obj, dict) else "N/A"
        team2_seed = team2_obj.get("seed", "N/A") if isinstance(team2_obj, dict) else "N/A"
        
        print(f"\nChampionship: {team1_name} (Seed {team1_seed}) vs {team2_name} (Seed {team2_seed}) -> {winner_name}")
        print(f"Reasoning: {championship.get('reasoning', 'No reasoning provided')[:200]}...")
    
    # Print Final Four
    if "5" in rounds and rounds["5"]:
        print("\nFinal Four:")
        for semifinal in rounds["5"]:
            team1_obj = semifinal.get("team1", {})
            team2_obj = semifinal.get("team2", {})
            winner_obj = semifinal.get("winner", {})
            
            team1_name = team1_obj.get("name", "Unknown") if isinstance(team1_obj, dict) else str(team1_obj)
            team2_name = team2_obj.get("name", "Unknown") if isinstance(team2_obj, dict) else str(team2_obj)
            winner_name = winner_obj.get("name", "Unknown") if isinstance(winner_obj, dict) else str(winner_obj)
            
            team1_seed = team1_obj.get("seed", "N/A") if isinstance(team1_obj, dict) else "N/A"
            team2_seed = team2_obj.get("seed", "N/A") if isinstance(team2_obj, dict) else "N/A"
            
            team1_region = semifinal.get("team1_region", "")
            team2_region = semifinal.get("team2_region", "")
            
            print(f"  {team1_name} (Seed {team1_seed}, {team1_region}) vs {team2_name} (Seed {team2_seed}, {team2_region}) -> {winner_name}")
    
    # Print Elite 8
    if "4" in rounds and rounds["4"]:
        print("\nElite 8:")
        for matchup in rounds["4"]:
            team1_obj = matchup.get("team1", {})
            team2_obj = matchup.get("team2", {})
            winner_obj = matchup.get("winner", {})
            
            team1_name = team1_obj.get("name", "Unknown") if isinstance(team1_obj, dict) else str(team1_obj)
            team2_name = team2_obj.get("name", "Unknown") if isinstance(team2_obj, dict) else str(team2_obj)
            winner_name = winner_obj.get("name", "Unknown") if isinstance(winner_obj, dict) else str(winner_obj)
            
            team1_seed = team1_obj.get("seed", "N/A") if isinstance(team1_obj, dict) else "N/A"
            team2_seed = team2_obj.get("seed", "N/A") if isinstance(team2_obj, dict) else "N/A"
            
            region = matchup.get("region", "Unknown")
            print(f"  {region}: {team1_name} (Seed {team1_seed}) vs {team2_name} (Seed {team2_seed}) -> {winner_name}")
    
    # If full bracket is requested, print all rounds
    if full_bracket:
        # Print Sweet 16 (Round 3)
        if "3" in rounds and rounds["3"]:
            print("\nSweet 16:")
            for matchup in rounds["3"]:
                team1_obj = matchup.get("team1", {})
                team2_obj = matchup.get("team2", {})
                winner_obj = matchup.get("winner", {})
                
                team1_name = team1_obj.get("name", "Unknown") if isinstance(team1_obj, dict) else str(team1_obj)
                team2_name = team2_obj.get("name", "Unknown") if isinstance(team2_obj, dict) else str(team2_obj)
                winner_name = winner_obj.get("name", "Unknown") if isinstance(winner_obj, dict) else str(winner_obj)
                
                team1_seed = team1_obj.get("seed", "N/A") if isinstance(team1_obj, dict) else "N/A"
                team2_seed = team2_obj.get("seed", "N/A") if isinstance(team2_obj, dict) else "N/A"
                
                region = matchup.get("region", "Unknown")
                print(f"  {region}: {team1_name} (Seed {team1_seed}) vs {team2_name} (Seed {team2_seed}) -> {winner_name}")
        
        # Print Round of 32 (Round 2)
        if "2" in rounds and rounds["2"]:
            print("\nRound of 32:")
            for matchup in rounds["2"]:
                team1_obj = matchup.get("team1", {})
                team2_obj = matchup.get("team2", {})
                winner_obj = matchup.get("winner", {})
                
                team1_name = team1_obj.get("name", "Unknown") if isinstance(team1_obj, dict) else str(team1_obj)
                team2_name = team2_obj.get("name", "Unknown") if isinstance(team2_obj, dict) else str(team2_obj)
                winner_name = winner_obj.get("name", "Unknown") if isinstance(winner_obj, dict) else str(winner_obj)
                
                team1_seed = team1_obj.get("seed", "N/A") if isinstance(team1_obj, dict) else "N/A"
                team2_seed = team2_obj.get("seed", "N/A") if isinstance(team2_obj, dict) else "N/A"
                
                region = matchup.get("region", "Unknown")
                print(f"  {region}: {team1_name} (Seed {team1_seed}) vs {team2_name} (Seed {team2_seed}) -> {winner_name}")
        
        # Print First Round (Round 1)
        if "1" in rounds and rounds["1"]:
            print("\nFirst Round:")
            for matchup in rounds["1"]:
                team1_obj = matchup.get("team1", {})
                team2_obj = matchup.get("team2", {})
                winner_obj = matchup.get("winner", {})
                
                team1_name = team1_obj.get("name", "Unknown") if isinstance(team1_obj, dict) else str(team1_obj)
                team2_name = team2_obj.get("name", "Unknown") if isinstance(team2_obj, dict) else str(team2_obj)
                winner_name = winner_obj.get("name", "Unknown") if isinstance(winner_obj, dict) else str(winner_obj)
                
                team1_seed = team1_obj.get("seed", "N/A") if isinstance(team1_obj, dict) else "N/A"
                team2_seed = team2_obj.get("seed", "N/A") if isinstance(team2_obj, dict) else "N/A"
                
                region = matchup.get("region", "Unknown")
                print(f"  {region}: {team1_name} (Seed {team1_seed}) vs {team2_name} (Seed {team2_seed}) -> {winner_name}")
    
    print("\n" + "=" * 80)

def list_result_files(model=None):
    """
    List all result files in the results directory.
    
    Args:
        model (str, optional): Filter results by model name
        
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
            # Skip combined results files
            if filename.startswith("all_results_"):
                continue
                
            # Filter by model if specified
            if model:
                model_lower = model.lower()
                if not filename.lower().startswith(model_lower):
                    continue
            
            result_files.append(os.path.join(results_dir, filename))
    
    return sorted(result_files)

def list_available_models():
    """
    List all available models from result files.
    
    Returns:
        list: List of model names
    """
    results_dir = "results"
    if not os.path.exists(results_dir):
        print(f"Results directory '{results_dir}' not found.")
        return []
    
    models = set()
    for filename in os.listdir(results_dir):
        if filename.endswith(".json") and not filename.startswith("all_results_"):
            # Extract model name from filename (everything before the first underscore)
            model = filename.split("_")[0].lower()
            models.add(model)
    
    return sorted(list(models))

def save_bracket_to_file(results, filename, full_bracket=False):
    """
    Save bracket visualization to a file.
    
    Args:
        results (dict): Bracket results
        filename (str): Path to save the file
        full_bracket (bool): Whether to include the full bracket with all rounds
    """
    # Redirect stdout to a string buffer
    import io
    import sys
    
    old_stdout = sys.stdout
    sys.stdout = mystdout = io.StringIO()
    
    # Print bracket to the buffer
    print_bracket(results, full_bracket)
    
    # Get the content and restore stdout
    output = mystdout.getvalue()
    sys.stdout = old_stdout
    
    # Save to file
    with open(filename, "w") as f:
        f.write(output)
    
    print(f"Bracket saved to {filename}")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Visualize NCAA March Madness bracket results.")
    parser.add_argument("--file", "-f", help="Path to the results file")
    parser.add_argument("--list", "-l", action="store_true", help="List available result files")
    parser.add_argument("--all", "-a", action="store_true", help="Visualize all result files")
    parser.add_argument("--model", "-m", help="Filter results by model name")
    parser.add_argument("--bracket", "-b", action="store_true", help="Print full bracket with all rounds")
    parser.add_argument("--models", action="store_true", help="List available models")
    parser.add_argument("--save", "-s", action="store_true", help="Save output to files in results directory")
    
    args = parser.parse_args()
    
    if args.models:
        models = list_available_models()
        if models:
            print("Available models:")
            for model in models:
                print(f"  {model}")
        else:
            print("No models found.")
        return
    
    if args.list:
        print("Available result files:")
        for filename in list_result_files(args.model):
            print(f"  {filename}")
        return
    
    if args.all:
        result_files = list_result_files(args.model)
        if not result_files:
            print("No result files found.")
            return
        
        for filename in result_files:
            results = load_results(filename)
            if results:
                if args.save:
                    # Create output filename based on input filename
                    model_name = os.path.basename(filename).split("_")[0]
                    output_filename = f"results/{model_name}_bracket{'_full' if args.bracket else ''}.txt"
                    save_bracket_to_file(results, output_filename, args.bracket)
                else:
                    print(f"\nResults from {filename}:")
                    print_bracket(results, args.bracket)
        return
    
    if args.file:
        filename = args.file
        if not os.path.exists(filename):
            print(f"File '{filename}' not found.")
            return
    else:
        # Use the most recent result file for the specified model or any model
        result_files = list_result_files(args.model)
        if not result_files:
            if args.model:
                print(f"No result files found for model '{args.model}'. Run the generator first.")
            else:
                print("No result files found. Run the generator first.")
            return
        
        filename = result_files[-1]
        print(f"Using most recent result file: {filename}")
    
    results = load_results(filename)
    if results:
        if args.save:
            # Create output filename based on input filename
            model_name = os.path.basename(filename).split("_")[0]
            output_filename = f"results/{model_name}_bracket{'_full' if args.bracket else ''}.txt"
            save_bracket_to_file(results, output_filename, args.bracket)
        else:
            print_bracket(results, args.bracket)

if __name__ == "__main__":
    main()
