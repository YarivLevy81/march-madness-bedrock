#!/usr/bin/env python3
"""
NCAA March Madness Bracket Generator using Amazon Bedrock models.
This script compares different Bedrock models' abilities to predict March Madness outcomes.
"""

import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
from tqdm import tqdm

from src.models.bedrock_client import BedrockClient
from src.models.agent import BracketAgent
from src.utils.bracket import Bracket
from src.utils.stats_retriever import StatsRetriever

# Load environment variables
load_dotenv()

# Models to test
MODELS = [
    {
        "name": "Claude 3.7 Sonnet",
        "model_id": "anthropic.claude-3-7-sonnet-20240620-v1:0",
    },
    {
        "name": "Llama 3.3 70B Instruct",
        "model_id": "meta.llama3-70b-instruct-v1:0",
    },
    {
        "name": "Mistral Large",
        "model_id": "mistral.mistral-large-2402-v1:0",
    },
    {
        "name": "DeepSeek-R1",
        "model_id": "deepseek.deepseek-coder-v1:0",
    },
    {
        "name": "Jamba 1.5 Large",
        "model_id": "ai21.jamba-1-5-large-v1:0",
    }
]

def main():
    print("NCAA March Madness 2025 Bracket Generator")
    print("========================================")
    
    # Initialize stats retriever
    stats_retriever = StatsRetriever(year=2025)
    
    # Load or create bracket structure
    bracket = Bracket(year=2025)
    
    # Create results directory if it doesn't exist
    os.makedirs("results", exist_ok=True)
    
    # Generate brackets for each model
    results = {}
    
    for model_config in tqdm(MODELS, desc="Testing models"):
        model_name = model_config["name"]
        model_id = model_config["model_id"]
        
        print(f"\nGenerating bracket using {model_name}...")
        
        # Initialize Bedrock client for this model
        bedrock_client = BedrockClient(model_id=model_id)
        
        # Create agent with this model
        agent = BracketAgent(
            model_client=bedrock_client,
            stats_retriever=stats_retriever
        )
        
        # Generate bracket
        start_time = time.time()
        completed_bracket = bracket.generate_with_agent(agent)
        end_time = time.time()
        
        # Save results
        results[model_name] = {
            "bracket": completed_bracket.to_dict(),
            "time_taken": end_time - start_time,
            "final_four": completed_bracket.get_final_four(),
            "champion": completed_bracket.get_champion()
        }
        
        # Save individual bracket to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results/{model_name.replace(' ', '_').lower()}_{timestamp}.json"
        
        with open(filename, "w") as f:
            json.dump(results[model_name], f, indent=2)
        
        print(f"Bracket saved to {filename}")
        print(f"Champion: {completed_bracket.get_champion()}")
        print(f"Time taken: {end_time - start_time:.2f} seconds")
    
    # Save combined results
    with open(f"results/all_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Compare results
    print("\nResults Summary:")
    print("===============")
    
    for model_name, result in results.items():
        print(f"\n{model_name}:")
        print(f"  Champion: {result['champion']}")
        print(f"  Final Four: {', '.join(result['final_four'])}")
        print(f"  Time taken: {result['time_taken']:.2f} seconds")

if __name__ == "__main__":
    main()
