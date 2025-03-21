#!/usr/bin/env python3
"""
Script to run a single model test for NCAA March Madness bracket generation.
"""

import os
import json
import time
import argparse
from datetime import datetime
from dotenv import load_dotenv

from src.models.bedrock_client import BedrockClient
from src.models.agent import BracketAgent
from src.utils.bracket import Bracket
from src.utils.stats_retriever import StatsRetriever

# Available models
AVAILABLE_MODELS = {
    "claude": {
        "name": "Claude 3.7 Sonnet",
        "model_id": "arn:aws:bedrock:us-east-1:273034491939:inference-profile/us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    },
    "llama": {
        "name": "Llama 3.3 70B Instruct",
        "model_id": "meta.llama3-70b-instruct-v1:0",
    },
    "mistral": {
        "name": "Mistral Large",
        "model_id": "mistral.mistral-large-2402-v1:0",
    },
    "nova": {
        "name": "Amazon Nova Pro",
        "model_id": "arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-pro-v1:0:300k",
    }
}

def run_model(model_key, year=2025, verbose=False):
    """
    Run a single model test.
    
    Args:
        model_key (str): Key of the model to test
        year (int): Tournament year
        verbose (bool): Whether to print verbose output
        
    Returns:
        dict: Results of the test
    """
    # Load environment variables
    load_dotenv()
    
    # Check if model is available
    if model_key not in AVAILABLE_MODELS:
        print(f"Error: Model '{model_key}' not found. Available models: {', '.join(AVAILABLE_MODELS.keys())}")
        return None
    
    model_config = AVAILABLE_MODELS[model_key]
    model_name = model_config["name"]
    model_id = model_config["model_id"]
    
    print(f"Running NCAA March Madness {year} bracket generation with {model_name}...")
    
    # Initialize stats retriever
    stats_retriever = StatsRetriever(year=year)
    
    # Load or create bracket structure
    bracket = Bracket(year=year)
    
    # Create results directory if it doesn't exist
    os.makedirs("results", exist_ok=True)
    
    # Initialize Bedrock client
    print(f"Initializing Bedrock client for {model_name}...")
    bedrock_client = BedrockClient(model_id=model_id)
    
    # Create agent
    agent = BracketAgent(
        model_client=bedrock_client,
        stats_retriever=stats_retriever
    )
    
    # Generate bracket
    print(f"Generating bracket...")
    start_time = time.time()
    completed_bracket = bracket.generate_with_agent(agent)
    end_time = time.time()
    
    # Save results
    results = {
        "bracket": completed_bracket.to_dict(),
        "time_taken": end_time - start_time,
        "final_four": completed_bracket.get_final_four(),
        "champion": completed_bracket.get_champion()
    }
    
    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"results/{model_key.lower()}_{timestamp}.json"
    
    with open(filename, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Bracket saved to {filename}")
    print(f"Champion: {completed_bracket.get_champion()}")
    print(f"Final Four: {', '.join(completed_bracket.get_final_four())}")
    print(f"Time taken: {end_time - start_time:.2f} seconds")
    
    return results

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Run a single model test for NCAA March Madness bracket generation.")
    parser.add_argument("model", choices=AVAILABLE_MODELS.keys(), help="Model to test")
    parser.add_argument("--year", type=int, default=2025, help="Tournament year")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print verbose output")
    
    args = parser.parse_args()
    
    run_model(args.model, args.year, args.verbose)

if __name__ == "__main__":
    main()
