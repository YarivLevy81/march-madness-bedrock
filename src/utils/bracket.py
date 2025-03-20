"""
Bracket module for managing NCAA tournament bracket structure and generation.
"""

import os
import json
import copy
import time
from datetime import datetime

class Bracket:
    """
    Manages NCAA tournament bracket structure and generation.
    """
    
    def __init__(self, year=2025, data_dir="src/data"):
        """
        Initialize the bracket.
        
        Args:
            year (int): The tournament year
            data_dir (str): Directory to store/load data files
        """
        self.year = year
        self.data_dir = data_dir
        self.bracket_file = os.path.join(data_dir, f"bracket_{year}.json")
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Load or create bracket structure
        self.structure = self._load_or_create_structure()
        
        # Initialize results
        self.results = {
            "rounds": {},
            "champion": None,
            "final_four": []
        }
    
    def generate_with_agent(self, agent):
        """
        Generate bracket picks using the provided agent.
        
        Args:
            agent (BracketAgent): Agent to use for predictions
            
        Returns:
            Bracket: Self with completed results
        """
        print(f"Generating {self.year} NCAA Tournament bracket...")
        
        # Create a deep copy of the bracket to avoid modifying the original
        bracket_copy = copy.deepcopy(self)
        
        # Process each round
        for round_num in range(1, 7):  # 6 rounds in the tournament
            print(f"\nProcessing Round {round_num}...")
            bracket_copy._process_round(round_num, agent)
        
        return bracket_copy
    
    def get_champion(self):
        """
        Get the predicted champion.
        
        Returns:
            str: Champion team name
        """
        return self.results.get("champion")
    
    def get_final_four(self):
        """
        Get the predicted Final Four teams.
        
        Returns:
            list: List of Final Four team names
        """
        return self.results.get("final_four", [])
    
    def to_dict(self):
        """
        Convert bracket to dictionary representation.
        
        Returns:
            dict: Dictionary representation of the bracket
        """
        return {
            "year": self.year,
            "structure": self.structure,
            "results": self.results
        }
    
    def save(self, filename=None):
        """
        Save bracket to file.
        
        Args:
            filename (str, optional): File to save to. Defaults to self.bracket_file.
        """
        if filename is None:
            filename = self.bracket_file
        
        with open(filename, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
    
    def _load_or_create_structure(self):
        """
        Load bracket structure from file or create a new one.
        
        Returns:
            dict: Bracket structure
        """
        if os.path.exists(self.bracket_file):
            try:
                with open(self.bracket_file, "r") as f:
                    data = json.load(f)
                    return data.get("structure", {})
            except Exception as e:
                print(f"Error loading bracket structure: {e}")
        
        # Create new bracket structure if file doesn't exist
        print(f"Creating new bracket structure for {self.year}...")
        return self._create_bracket_structure()
    
    def _create_bracket_structure(self):
        """
        Create a new bracket structure.
        
        Returns:
            dict: Bracket structure
        """
        # Load team information from a file if it exists
        teams_file = os.path.join(self.data_dir, f"teams_{self.year}.json")
        teams = {}
        
        if os.path.exists(teams_file):
            try:
                with open(teams_file, "r") as f:
                    teams = json.load(f)
            except Exception as e:
                print(f"Error loading team information: {e}")
        
        # Create bracket structure
        structure = {
            "regions": {
                "East": self._create_region_structure("East", teams),
                "West": self._create_region_structure("West", teams),
                "South": self._create_region_structure("South", teams),
                "Midwest": self._create_region_structure("Midwest", teams)
            },
            "final_four": {
                "semifinals": [
                    {"team1_region": "East", "team2_region": "West"},
                    {"team1_region": "South", "team2_region": "Midwest"}
                ],
                "championship": {}
            }
        }
        
        return structure
    
    def _create_region_structure(self, region_name, teams):
        """
        Create structure for a single region.
        
        Args:
            region_name (str): Name of the region
            teams (dict): Team information
            
        Returns:
            dict: Region structure
        """
        # Find teams in this region
        region_teams = {}
        for team_name, team_info in teams.items():
            if team_info.get("region") == region_name:
                seed = team_info.get("seed")
                if seed:
                    region_teams[seed] = {
                        "name": team_name,
                        "seed": seed
                    }
        
        # If we don't have enough teams, create placeholders
        for seed in range(1, 17):
            if seed not in region_teams:
                region_teams[seed] = {
                    "name": f"{region_name} Seed {seed}",
                    "seed": seed
                }
        
        # Create first round matchups
        first_round = [
            {"team1": region_teams[1], "team2": region_teams[16]},
            {"team1": region_teams[8], "team2": region_teams[9]},
            {"team1": region_teams[5], "team2": region_teams[12]},
            {"team1": region_teams[4], "team2": region_teams[13]},
            {"team1": region_teams[6], "team2": region_teams[11]},
            {"team1": region_teams[3], "team2": region_teams[14]},
            {"team1": region_teams[7], "team2": region_teams[10]},
            {"team1": region_teams[2], "team2": region_teams[15]}
        ]
        
        # Create empty structures for later rounds
        # These are just placeholders as we now use a different approach to determine matchups
        second_round = [{}, {}, {}, {}]
        sweet_16 = [{}, {}]
        elite_8 = [{}]
        
        return {
            "rounds": {
                "1": first_round,
                "2": second_round,
                "3": sweet_16,
                "4": elite_8
            }
        }
    
    def _process_round(self, round_num, agent):
        """
        Process a single round of the tournament.
        
        Args:
            round_num (int): Round number (1-6)
            agent (BracketAgent): Agent to use for predictions
        """
        # Initialize round results if not already present
        if str(round_num) not in self.results["rounds"]:
            self.results["rounds"][str(round_num)] = []
        
        if round_num <= 4:
            # Rounds 1-4 are region-specific
            for region_name, region in self.structure["regions"].items():
                print(f"  Processing {region_name} region...")
                self._process_region_round(round_num, region_name, agent)
        elif round_num == 5:
            # Round 5 is Final Four semifinals
            print("  Processing Final Four semifinals...")
            self._process_final_four(agent)
        elif round_num == 6:
            # Round 6 is the championship game
            print("  Processing Championship game...")
            self._process_championship(agent)
    
    def _predict_winner_with_retry(self, team1, team2, round_num, agent, team1_region=None, team2_region=None):
        """
        Predict winner with retry logic and exponential backoff.
        
        Args:
            team1 (dict): First team
            team2 (dict): Second team
            round_num (int): Tournament round number
            agent (BracketAgent): Agent to use for predictions
            team1_region (str, optional): Region of team1 (for Final Four and Championship)
            team2_region (str, optional): Region of team2 (for Final Four and Championship)
            
        Returns:
            tuple: (winner, winner_region, prediction) - winner is the winning team dict,
                  winner_region is the region (only for Final Four and Championship),
                  prediction is the full prediction dict from the agent
        """
        max_attempts = 5
        attempts = 0
        winner = None
        winner_region = None
        prediction = agent.predict_winner(team1, team2, round_num)
        
        while attempts < max_attempts and winner is None:
            attempts += 1
            
            # Only retry after the first attempt
            if attempts > 1:
                # Exponential backoff: wait time increases with each attempt
                backoff_time = 0.5 * (2 ** (attempts - 2))  # 0.5, 1, 2, 4 seconds
                print(f"      Retry attempt {attempts} for prediction (waiting {backoff_time:.1f}s)...")
                time.sleep(backoff_time)
                prediction = agent.predict_winner(team1, team2, round_num)
            
            winner_name = prediction["prediction"].strip()
            
            # Normalize team names for comparison
            team1_normalized = self._normalize_team_name(team1["name"])
            team2_normalized = self._normalize_team_name(team2["name"])
            winner_normalized = self._normalize_team_name(winner_name)
            
            # Determine winner based on normalized prediction
            if team1_normalized in winner_normalized or winner_normalized in team1_normalized:
                winner = team1
                winner_region = team1_region
            elif team2_normalized in winner_normalized or winner_normalized in team2_normalized:
                winner = team2
                winner_region = team2_region
            else:
                if attempts < max_attempts:
                    print(f"      Could not determine winner from prediction '{winner_name}'. Retrying...")
                else:
                    print(f"      Failed to determine winner after {max_attempts} attempts. Failing process.")
                    raise ValueError(f"Failed to determine winner for {team1['name']} vs {team2['name']} after {max_attempts} attempts")
        
        return winner, winner_region, prediction
    
    def _normalize_team_name(self, team_name):
        """
        Normalize team name for more robust matching.
        
        Args:
            team_name (str): Team name to normalize
            
        Returns:
            str: Normalized team name
        """
        # Convert to lowercase
        normalized = team_name.lower()
        
        # Replace common abbreviations
        normalized = normalized.replace("st.", "st")
        normalized = normalized.replace("st ", "st")
        
        # Remove apostrophes and periods
        normalized = normalized.replace("'", "")
        normalized = normalized.replace(".", "")
        
        # Remove other special characters and extra spaces
        normalized = ''.join(c for c in normalized if c.isalnum() or c.isspace())
        normalized = ' '.join(normalized.split())
        
        return normalized
        
    def _process_region_round(self, round_num, region_name, agent):
        """
        Process a single round within a region.
        
        Args:
            round_num (int): Round number (1-4)
            region_name (str): Region name
            agent (BracketAgent): Agent to use for predictions
        """
        region = self.structure["regions"][region_name]
        round_key = str(round_num)
        prev_round_key = str(round_num - 1)
        
        # Get matchups for this round
        matchups = region["rounds"].get(round_key, [])
        
        for i, matchup in enumerate(matchups):
            if round_num == 1:
                # First round has explicit team1 and team2
                team1 = matchup["team1"]
                team2 = matchup["team2"]
            else:
                # Later rounds reference winners of previous matchups
                prev_round_results = self.results["rounds"][prev_round_key]
                
                # Calculate the indices of the two previous matchups that feed into this one
                # For round 2: matchup 0 gets winners from previous matchups 0 and 1
                #              matchup 1 gets winners from previous matchups 2 and 3
                # For round 3: matchup 0 gets winners from previous matchups 0 and 1
                # For round 4: matchup 0 gets winners from previous matchups 0 and 1
                prev_idx1 = i * 2
                prev_idx2 = i * 2 + 1
                
                # Find the first previous matchup result
                prev_matchup_result1 = None
                for result in prev_round_results:
                    if (result["region"] == region_name and 
                        result["matchup_index"] == prev_idx1 and
                        result["round"] == round_num - 1):
                        prev_matchup_result1 = result
                        break
                
                if not prev_matchup_result1:
                    print(f"Error: Could not find previous matchup result for {region_name} round {round_num} matchup {i}, previous index {prev_idx1}")
                    continue
                
                # Find the second previous matchup result
                prev_matchup_result2 = None
                for result in prev_round_results:
                    if (result["region"] == region_name and 
                        result["matchup_index"] == prev_idx2 and
                        result["round"] == round_num - 1):
                        prev_matchup_result2 = result
                        break
                
                if not prev_matchup_result2:
                    print(f"Error: Could not find previous matchup result for {region_name} round {round_num} matchup {i}, previous index {prev_idx2}")
                    continue
                
                # Get the teams for this matchup
                team1 = prev_matchup_result1["winner"]
                team2 = prev_matchup_result2["winner"]
            
            # Predict winner with retry logic
            print(f"    Matchup: {team1['name']} (Seed {team1['seed']}) vs {team2['name']} (Seed {team2['seed']})")
            winner, _, prediction = self._predict_winner_with_retry(team1, team2, round_num, agent)
            
            print(f"      Winner: {winner['name']} (Seed {winner['seed']})")
            print(f"      Reasoning: {prediction['reasoning'][:100]}...")
            
            # Store result
            result = {
                "round": round_num,
                "region": region_name,
                "matchup_index": i,
                "team1": team1,
                "team2": team2,
                "winner": winner,
                "reasoning": prediction["reasoning"],
                "analysis": prediction["analysis"],
                "raw_prediction": prediction["raw_response"]
            }
            
            self.results["rounds"][round_key].append(result)
            
            # If this is the Elite 8 (round 4), add winner to Final Four
            if round_num == 4:
                self.results["final_four"].append(winner["name"])
    
    def _process_final_four(self, agent):
        """
        Process the Final Four semifinals.
        
        Args:
            agent (BracketAgent): Agent to use for predictions
        """
        # Get the Final Four teams from each region
        final_four_teams = {}
        for region_name in ["East", "West", "South", "Midwest"]:
            # Find the Elite 8 result for this region
            for result in self.results["rounds"]["4"]:
                if result["region"] == region_name:
                    final_four_teams[region_name] = result["winner"]
                    break
        
        # Process each semifinal matchup
        for i, matchup in enumerate(self.structure["final_four"]["semifinals"]):
            team1_region = matchup["team1_region"]
            team2_region = matchup["team2_region"]
            
            team1 = final_four_teams.get(team1_region)
            team2 = final_four_teams.get(team2_region)
            
            if not team1 or not team2:
                print(f"Error: Missing Final Four team for {team1_region} vs {team2_region}")
                continue
            
            # Predict winner with retry logic
            print(f"    Matchup: {team1['name']} ({team1_region}) vs {team2['name']} ({team2_region})")
            winner, winner_region, prediction = self._predict_winner_with_retry(
                team1, team2, 5, agent, team1_region, team2_region
            )
            
            print(f"      Winner: {winner['name']} ({winner_region})")
            print(f"      Reasoning: {prediction['reasoning'][:100]}...")
            
            # Store result
            result = {
                "round": 5,
                "matchup_index": i,
                "team1": team1,
                "team1_region": team1_region,
                "team2": team2,
                "team2_region": team2_region,
                "winner": winner,
                "winner_region": winner_region,
                "reasoning": prediction["reasoning"],
                "analysis": prediction["analysis"],
                "raw_prediction": prediction["raw_response"]
            }
            
            # Initialize round results if not already present
            if "5" not in self.results["rounds"]:
                self.results["rounds"]["5"] = []
            
            self.results["rounds"]["5"].append(result)
            
            # Update championship matchup
            if i == 0:
                self.structure["final_four"]["championship"]["team1_region"] = winner_region
            else:
                self.structure["final_four"]["championship"]["team2_region"] = winner_region
    
    def _process_championship(self, agent):
        """
        Process the championship game.
        
        Args:
            agent (BracketAgent): Agent to use for predictions
        """
        # Get the championship teams from the semifinals
        championship_teams = {}
        for result in self.results["rounds"]["5"]:
            region = result["winner_region"]
            championship_teams[region] = result["winner"]
        
        # Get the regions for the championship game
        team1_region = self.structure["final_four"]["championship"].get("team1_region")
        team2_region = self.structure["final_four"]["championship"].get("team2_region")
        
        if not team1_region or not team2_region:
            print("Error: Missing championship team regions")
            return
        
        team1 = championship_teams.get(team1_region)
        team2 = championship_teams.get(team2_region)
        
        if not team1 or not team2:
            print(f"Error: Missing championship team for {team1_region} vs {team2_region}")
            return
        
        # Predict winner with retry logic
        print(f"    Championship: {team1['name']} ({team1_region}) vs {team2['name']} ({team2_region})")
        winner, winner_region, prediction = self._predict_winner_with_retry(
            team1, team2, 6, agent, team1_region, team2_region
        )
        
        print(f"      Champion: {winner['name']} ({winner_region})")
        print(f"      Reasoning: {prediction['reasoning'][:100]}...")
        
        # Store result
        result = {
            "round": 6,
            "team1": team1,
            "team1_region": team1_region,
            "team2": team2,
            "team2_region": team2_region,
            "winner": winner,
            "winner_region": winner_region,
            "reasoning": prediction["reasoning"],
            "analysis": prediction["analysis"],
            "raw_prediction": prediction["raw_response"]
        }
        
        # Initialize round results if not already present
        if "6" not in self.results["rounds"]:
            self.results["rounds"]["6"] = []
        
        self.results["rounds"]["6"].append(result)
        
        # Set champion
        self.results["champion"] = winner["name"]
