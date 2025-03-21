"""
BracketAgent module for making NCAA bracket predictions using LLMs.
"""

import json
import re

class BracketAgent:
    """
    Agent that uses LLMs to predict NCAA tournament outcomes.
    """
    
    def __init__(self, model_client, stats_retriever):
        """
        Initialize the bracket agent.
        
        Args:
            model_client (BedrockClient): Client for interacting with the LLM
            stats_retriever (StatsRetriever): Tool for retrieving team statistics
        """
        self.model_client = model_client
        self.stats_retriever = stats_retriever
        
        # System prompt to guide the model's behavior
        self.system_prompt = """
        You are an expert NCAA basketball analyst tasked with predicting March Madness tournament outcomes.
        
        For each matchup:
        1. Analyze the statistics of both teams objectively
        2. Consider factors like offensive efficiency, defensive efficiency, strength of schedule, etc.
        3. Provide clear reasoning for your prediction
        4. Make a final prediction on which team will win
        
        Your response MUST follow this exact format:
        
        ANALYSIS:
        [Your detailed analysis of both teams, comparing their strengths and weaknesses]
        
        REASONING:
        [Your reasoning for why one team has an advantage over the other]
        
        PREDICTION:
        [EXACT team name - just the name of the winning team, nothing else]
        
        IMPORTANT: In the PREDICTION section, provide ONLY the exact name of the winning team (e.g., "Duke" or "Michigan State"). Do not include any additional text, explanations, or qualifiers in this section.
        """
    
    def predict_winner(self, team1, team2, round_number):
        """
        Predict the winner of a matchup between two teams.
        
        Args:
            team1 (dict): First team information (name, seed, etc.)
            team2 (dict): Second team information (name, seed, etc.)
            round_number (int): The tournament round number (1-6)
            
        Returns:
            dict: Prediction result with winner and reasoning
        """
        # Get statistics for both teams
        team1_stats = self.stats_retriever.get_team_stats(team1["name"])
        team2_stats = self.stats_retriever.get_team_stats(team2["name"])
        
        # Format prompt with team information and statistics
        prompt = self._format_prediction_prompt(team1, team1_stats, team2, team2_stats, round_number)
        
        # Get prediction from model
        response = self.model_client.invoke(
            prompt=prompt,
            system_prompt=self.system_prompt,
            temperature=0.3  # Lower temperature for more consistent predictions
        )
        
        # Parse the response to extract reasoning and prediction
        parsed_result = self._parse_prediction_response(response)
        
        # Add team information to the result
        parsed_result["team1"] = team1
        parsed_result["team2"] = team2
        
        return parsed_result
    
    def _format_prediction_prompt(self, team1, team1_stats, team2, team2_stats, round_number):
        """
        Format the prompt for predicting a matchup winner.
        
        Args:
            team1 (dict): First team information
            team1_stats (dict): First team statistics
            team2 (dict): Second team information
            team2_stats (dict): Second team statistics
            round_number (int): Tournament round number
            
        Returns:
            str: Formatted prompt
        """
        round_names = {
            1: "First Round",
            2: "Second Round",
            3: "Sweet 16",
            4: "Elite 8",
            5: "Final Four",
            6: "Championship"
        }
        
        round_name = round_names.get(round_number, f"Round {round_number}")
        
        prompt = f"""
        NCAA March Madness 2025 - {round_name} Matchup
        
        Team 1: {team1['name']} (Seed: {team1.get('seed', 'N/A')})
        {self._format_team_stats(team1_stats)}
        
        Team 2: {team2['name']} (Seed: {team2.get('seed', 'N/A')})
        {self._format_team_stats(team2_stats)}
        
        Based on the statistics above, analyze both teams and predict which team will win this {round_name} matchup.
        
        Remember to follow the exact format:
        1. ANALYSIS: (detailed comparison)
        2. REASONING: (why one team has the advantage)
        3. PREDICTION: (ONLY the exact name of the winning team - either "{team1['name']}" or "{team2['name']}")
        
        Your prediction must be clear and unambiguous.
        """
        
        return prompt
    
    def _format_team_stats(self, stats):
        """
        Format team statistics for the prompt.
        
        Args:
            stats (dict): Team statistics
            
        Returns:
            str: Formatted statistics string
        """
        if not stats:
            return "Statistics not available."
        
        formatted_stats = []
        
        # Format key statistics
        for key, value in stats.items():
            # Format the key for display (convert snake_case to Title Case)
            display_key = key.replace('_', ' ').title()
            
            # Format the value based on its type
            if isinstance(value, float):
                formatted_value = f"{value:.2f}"
            else:
                formatted_value = str(value)
            
            formatted_stats.append(f"{display_key}: {formatted_value}")
        
        return "\n".join(formatted_stats)
    
    def _parse_prediction_response(self, response):
        """
        Parse the model's response to extract reasoning and prediction.
        
        Args:
            response (str): Model's response text
            
        Returns:
            dict: Parsed prediction with reasoning and winner
        """
        result = {
            "analysis": "",
            "reasoning": "",
            "prediction": "",
            "raw_response": response
        }
        
        # Extract analysis
        analysis_match = re.search(r"ANALYSIS:(.*?)(?=REASONING:|$)", response, re.DOTALL)
        if analysis_match:
            result["analysis"] = analysis_match.group(1).strip()
        
        # Extract reasoning
        reasoning_match = re.search(r"REASONING:(.*?)(?=PREDICTION:|$)", response, re.DOTALL)
        if reasoning_match:
            result["reasoning"] = reasoning_match.group(1).strip()
        
        # Extract prediction - try multiple patterns
        prediction_match = re.search(r"PREDICTION:(.*?)$", response, re.DOTALL)
        if prediction_match:
            result["prediction"] = prediction_match.group(1).strip()
        
        # If we couldn't parse the structured format, try to extract the team name from the last few lines
        if not result["prediction"]:
            # Get the last non-empty line as a fallback prediction
            lines = [line.strip() for line in response.split("\n") if line.strip()]
            if lines:
                result["prediction"] = lines[-1]
        
        return result
