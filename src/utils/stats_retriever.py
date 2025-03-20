"""
StatsRetriever module for fetching NCAA basketball team statistics.
"""

import os
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StatsRetriever:
    """
    Retrieves and provides NCAA basketball team statistics from JSON files.
    """
    
    def __init__(self, data_dir="src/data", year=2025):
        """
        Initialize the stats retriever.
        
        Args:
            data_dir (str): Directory to store/load data files
            year (int): The tournament year
        """
        self.data_dir = data_dir
        self.year = year
        self.stats_file = os.path.join(data_dir, f"team_stats_{year}.json")
        self.teams_file = os.path.join(data_dir, f"teams_{year}.json")
        self.cache_expiry = 24 * 60 * 60  # 24 hours in seconds
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Load team statistics
        self.team_stats = self._load_stats()
        
        # Load team information
        self.teams = self._load_teams()
    
    def get_team_stats(self, team_name):
        """
        Get statistics for a specific team.
        
        Args:
            team_name (str): The name of the team
            
        Returns:
            dict: Team statistics or empty dict if not found
        """
        # Try to find an exact match
        if team_name in self.team_stats:
            return self.team_stats[team_name]
        
        # Try case-insensitive match
        team_name_lower = team_name.lower()
        for name, stats in self.team_stats.items():
            if name.lower() == team_name_lower:
                return stats
        
        # Try to find a partial match
        for name, stats in self.team_stats.items():
            if team_name_lower in name.lower() or name.lower() in team_name_lower:
                return stats
        
        # Return empty dict if team not found
        logger.warning(f"No statistics found for team '{team_name}'")
        return {}
    
    def get_team_info(self, team_name):
        """
        Get information for a specific team.
        
        Args:
            team_name (str): The name of the team
            
        Returns:
            dict: Team information or empty dict if not found
        """
        # Try to find an exact match
        if team_name in self.teams:
            return self.teams[team_name]
        
        # Try case-insensitive match
        team_name_lower = team_name.lower()
        for name, info in self.teams.items():
            if name.lower() == team_name_lower:
                return info
        
        # Try to find a partial match
        for name, info in self.teams.items():
            if team_name_lower in name.lower() or name.lower() in team_name_lower:
                return info
        
        # Return empty dict if team not found
        logger.warning(f"No information found for team '{team_name}'")
        return {}
    
    def _load_stats(self):
        """
        Load team statistics from individual team JSON files only.
        
        Returns:
            dict: Team statistics
        """
        # Load from individual team JSON files
        team_stats_dir = os.path.join(self.data_dir, "team_stats")
        if os.path.exists(team_stats_dir):
            logger.info(f"Loading team stats from individual JSON files in: {team_stats_dir}")
            stats = self._load_stats_from_team_files(team_stats_dir)
            if stats:
                logger.info(f"Successfully loaded stats for {len(stats)} teams from individual JSON files")
                
                # Save to combined cache file for future use
                with open(self.stats_file, "w") as f:
                    json.dump(stats, f, indent=2)
                logger.info(f"Saved combined team stats to cache: {self.stats_file}")
                
                return stats
            else:
                logger.error(f"No team stats found in {team_stats_dir}")
                return {}
        else:
            logger.error(f"Team stats directory not found: {team_stats_dir}")
            return {}
    
    def _load_teams(self):
        """
        Load team information from individual team JSON files only.
        
        Returns:
            dict: Team information
        """
        # Extract team information from the team stats
        teams = {}
        
        # If we have team stats loaded, extract team info from there
        if hasattr(self, 'team_stats') and self.team_stats:
            logger.info("Extracting team information from team stats")
            
            for team_name, stats in self.team_stats.items():
                # Create a team info object with available data from stats
                teams[team_name] = {
                    "name": team_name,
                    "seed": stats.get("seed", 0),
                    "region": stats.get("region", "Unknown")
                }
            
            # Save to cache for future use
            if teams:
                with open(self.teams_file, "w") as f:
                    json.dump(teams, f, indent=2)
                logger.info(f"Saved team info to cache: {self.teams_file}")
            
            return teams
        else:
            logger.error("No team stats available to extract team information")
            return {}
    
    def _load_stats_from_team_files(self, team_stats_dir):
        """
        Load team statistics from individual JSON files in the team_stats directory.
        
        Args:
            team_stats_dir (str): Path to the directory containing team JSON files
            
        Returns:
            dict: Combined team statistics
        """
        logger.info(f"Loading team statistics from individual files in {team_stats_dir}")
        stats = {}
        
        try:
            # Get list of all JSON files in the directory
            team_files = [f for f in os.listdir(team_stats_dir) if f.endswith('.json')]
            
            if not team_files:
                logger.warning(f"No JSON files found in {team_stats_dir}")
                return {}
            
            # Process each team file
            for team_file in team_files:
                team_name = os.path.splitext(team_file)[0]  # Remove .json extension
                file_path = os.path.join(team_stats_dir, team_file)
                
                try:
                    with open(file_path, 'r') as f:
                        team_data = json.load(f)
                        
                    # Store the team stats
                    stats[team_name] = team_data
                    
                except Exception as e:
                    logger.error(f"Error loading team stats from {file_path}: {e}")
            
            logger.info(f"Successfully loaded stats for {len(stats)} teams from individual files")
            return stats
            
        except Exception as e:
            logger.error(f"Error loading team stats from directory {team_stats_dir}: {e}")
            return {}
