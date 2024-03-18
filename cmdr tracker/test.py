import json

# Load suggestions
with open("player_names.txt", "r") as file:
     player_names = file.read().splitlines()
player_names_suggestions = json.dumps(player_names)

print(player_names_suggestions)
