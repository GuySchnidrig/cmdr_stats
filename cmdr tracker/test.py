from flask import Flask, render_template, request, jsonify
import time
import pandas as pd

# Initial life totals for 4 players
players_life = {'Player 1': 40, 'Player 2': 40, 'Player 3': 40, 'Player 4': 40}

# Initial active player and turn count
active_player_index = 0
turn_count = 1
start_time = None
turn_time = None
start_turn_time = None

# Create a pandas DataFrame to store turn times per player
turn_times_df = pd.DataFrame(columns=players_life.keys())

print(turn_times_df)
