import json
import os

class PlayerAchievementService:
    def __init__(self, filename="achievements.json"):
        # Put the file in the same directory as the executable/main.py
        self.filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), filename)
        self.stats = self.load_stats()

    def load_stats(self):
        if not os.path.exists(self.filepath):
            return {"players": {}}
        
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            # If file is corrupted or cannot be read, return empty stats
            print("Warning: Could not read achievements file. Starting fresh.")
            return {"players": {}}

    def save_stats(self):
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=4)
        except IOError:
            print("Warning: Could not save achievements file.")

    def ensure_player(self, username):
        username = username.strip()
        if "players" not in self.stats:
            self.stats["players"] = {}
            
        if username not in self.stats["players"]:
            self.stats["players"][username] = {
                "wins": 0,
                "losses": 0
            }

    def record_win(self, username):
        username = username.strip()
        self.ensure_player(username)
        self.stats["players"][username]["wins"] += 1
        self.save_stats()

    def record_loss(self, username):
        username = username.strip()
        self.ensure_player(username)
        self.stats["players"][username]["losses"] += 1
        self.save_stats()

    def get_player_stats(self, username):
        username = username.strip()
        self.ensure_player(username)
        return self.stats["players"][username]
