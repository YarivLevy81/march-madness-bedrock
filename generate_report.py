#!/usr/bin/env python3
"""
Script to generate a detailed report of NCAA March Madness bracket predictions.
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

def generate_report(all_results, output_file=None):
    """
    Generate a detailed report of the bracket predictions.
    
    Args:
        all_results (dict): Dictionary of model name to results
        output_file (str, optional): Path to save the report
    """
    if not all_results:
        print("No results to report.")
        return
    
    # Prepare report
    report = []
    report.append("# NCAA March Madness Bracket Prediction Report")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Summary table
    report.append("## Summary")
    report.append("")
    
    summary_data = []
    headers = ["Model", "Champion", "Final Four", "Regions", "Upsets", "Time"]
    
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
        
        summary_data.append([
            model_name,
            champion,
            ", ".join(final_four[:4]),  # Limit to 4 teams
            len(regions),
            upset_count,
            f"{time_taken:.2f}s" if time_taken else "N/A"
        ])
    
    report.append(tabulate(summary_data, headers=headers, tablefmt="pipe"))
    report.append("")
    
    # Model details
    for model_name, results in all_results.items():
        report.append(f"## {model_name}")
        report.append("")
        
        # Champion
        champion = results.get("champion", "Unknown")
        report.append(f"### Champion: {champion}")
        report.append("")
        
        # Final Four
        final_four = results.get("final_four", [])
        report.append("### Final Four")
        for team in final_four:
            report.append(f"- {team}")
        report.append("")
        
        # Championship game
        if isinstance(results.get("bracket"), dict):
            rounds = results["bracket"].get("results", {}).get("rounds", {})
            if "6" in rounds and rounds["6"]:
                championship = rounds["6"][0]
                team1 = championship.get("team1", {}).get("name", "Unknown")
                team2 = championship.get("team2", {}).get("name", "Unknown")
                winner = championship.get("winner", {}).get("name", "Unknown")
                reasoning = championship.get("reasoning", "No reasoning provided")
                
                report.append("### Championship Game")
                report.append(f"**{team1}** vs **{team2}** → **{winner}**")
                report.append("")
                report.append("#### Reasoning")
                report.append(reasoning)
                report.append("")
        
        # Upset analysis
        if isinstance(results.get("bracket"), dict):
            rounds = results["bracket"].get("results", {}).get("rounds", {})
            upsets = []
            
            for round_key, matchups in rounds.items():
                for matchup in matchups:
                    team1 = matchup.get("team1", {})
                    team2 = matchup.get("team2", {})
                    winner = matchup.get("winner", {})
                    
                    # Check if this is an upset
                    if (team1.get("seed") and team2.get("seed") and winner.get("seed")):
                        if team1.get("seed") < team2.get("seed") and winner.get("name") == team2.get("name"):
                            upsets.append({
                                "round": round_key,
                                "favorite": team1.get("name"),
                                "favorite_seed": team1.get("seed"),
                                "underdog": team2.get("name"),
                                "underdog_seed": team2.get("seed"),
                                "reasoning": matchup.get("reasoning", "")
                            })
                        elif team2.get("seed") < team1.get("seed") and winner.get("name") == team1.get("name"):
                            upsets.append({
                                "round": round_key,
                                "favorite": team2.get("name"),
                                "favorite_seed": team2.get("seed"),
                                "underdog": team1.get("name"),
                                "underdog_seed": team1.get("seed"),
                                "reasoning": matchup.get("reasoning", "")
                            })
            
            if upsets:
                report.append("### Notable Upsets")
                for upset in upsets:
                    report.append(f"**Round {upset['round']}:** #{upset['underdog_seed']} {upset['underdog']} defeats #{upset['favorite_seed']} {upset['favorite']}")
                    report.append(f"*Reasoning:* {upset['reasoning'][:200]}...")
                    report.append("")
        
        report.append("---")
        report.append("")
    
    # Model comparison
    report.append("## Model Comparison")
    report.append("")
    
    # Compare Final Four picks
    report.append("### Final Four Picks")
    ff_data = []
    for model_name, results in all_results.items():
        final_four = results.get("final_four", [])
        ff_data.append([model_name] + final_four[:4])
    
    ff_headers = ["Model", "Team 1", "Team 2", "Team 3", "Team 4"]
    report.append(tabulate(ff_data, headers=ff_headers, tablefmt="pipe"))
    report.append("")
    
    # Compare reasoning approaches
    report.append("### Reasoning Comparison")
    report.append("")
    report.append("This section compares how different models approach their reasoning for key matchups.")
    report.append("")
    
    # Find a common matchup across all models
    common_matchup = None
    if all(isinstance(results.get("bracket"), dict) for results in all_results.values()):
        # Try to find championship game
        for model_name, results in all_results.items():
            rounds = results["bracket"].get("results", {}).get("rounds", {})
            if "6" in rounds and rounds["6"]:
                championship = rounds["6"][0]
                team1 = championship.get("team1", {}).get("name", "Unknown")
                team2 = championship.get("team2", {}).get("name", "Unknown")
                common_matchup = (team1, team2)
                break
    
    if common_matchup:
        report.append(f"#### Championship: {common_matchup[0]} vs {common_matchup[1]}")
        report.append("")
        
        for model_name, results in all_results.items():
            if isinstance(results.get("bracket"), dict):
                rounds = results["bracket"].get("results", {}).get("rounds", {})
                if "6" in rounds and rounds["6"]:
                    championship = rounds["6"][0]
                    reasoning = championship.get("reasoning", "No reasoning provided")
                    
                    report.append(f"**{model_name}:**")
                    report.append(reasoning[:300] + "..." if len(reasoning) > 300 else reasoning)
                    report.append("")
    
    # Save report
    report_text = "\n".join(report)
    
    if output_file:
        with open(output_file, "w") as f:
            f.write(report_text)
        print(f"Report saved to {output_file}")
    else:
        print(report_text)

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Generate a detailed report of NCAA March Madness bracket predictions.")
    parser.add_argument("--output", "-o", help="Output file path (default: report_YYYYMMDD_HHMMSS.md)")
    
    args = parser.parse_args()
    
    print("Generating NCAA March Madness bracket prediction report...")
    all_results = load_all_results()
    
    if not all_results:
        print("No results found. Run the generator first.")
        return
    
    # Set output file if not provided
    output_file = args.output
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"report_{timestamp}.md"
    
    generate_report(all_results, output_file)

if __name__ == "__main__":
    main()
