# Import libraries
from flask import Flask, render_template, request, Response, jsonify
import time
import csv
from io import StringIO
import os
from datetime import datetime

app = Flask(__name__)

# Initate players
players_life = {'Player 1': 40, 'Player 2': 40, 'Player 3': 40, 'Player 4': 40}
players_time = {'Player 1': 0, 'Player 2': 0, 'Player 3': 0, 'Player 4': 0}
players_decks = {'Player 1': "Default1", 'Player 2': "Default1", 'Player 3': "Default1", 'Player 4': "Default1"}
players_win = {'Player 1': 0, 'Player 2': 0, 'Player 3': 0, 'Player 4': 0}
players_start = {'Player 1': 0, 'Player 2': 0, 'Player 3': 0, 'Player 4': 0}

# Initial active player, turn count, start_time, turn_time, start_turn_time
active_player_index = 0
turn_count = 1
start_time = None
turn_time = None
start_turn_time = None
new_game_id = 0

# Load suggestions
def read_txt_file(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    return [line.strip() for line in lines]

# Function to save CSV data to a file on the server
def save_csv(data):
    folder_path = "data/"
    filename = os.path.join(folder_path, "game_data.csv")
    with open(filename, "a", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        for idx, row in enumerate(data):
            if idx == 0:  # Skip the first row (header)
                continue
            csv_writer.writerow(row)
 
def read_last_game_id(filename):
    folder_path = "data/"
    filename = os.path.join(folder_path, "game_data.csv")
    # Initialize the variable to hold the last Game ID
    last_game_id = None

    # Read the CSV file
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        
        # Iterate through each row in the CSV file
        for row in reader:
            last_game_id = int(row['Game_ID'])  # Update last Game ID for each iteration

    return last_game_id



@app.route('/')
def index():
    global active_player_index, turn_count
    
    active_player_index = 0
    turn_count = 1
    
    player_names_suggestions = read_txt_file('player_names.txt')  
    commander_names_suggestions = read_txt_file('commander_names.txt')    

    return render_template('enter_players.html', commander_names_suggestions = commander_names_suggestions, player_names_suggestions = player_names_suggestions, 
                           active_player_index = active_player_index, turn_count = turn_count, players_startt = players_start)

@app.route('/submit_players', methods=['POST'])
def submit_players():
    global players_life, start_time, turn_time, start_turn_time, player_names, active_player_index, players_time, deck_names, players_decks, players_win, players_start, last_game_id
    
    num_players = int(request.form['num_players'])
    
    players_life = {request.form[f'player{i+1}']: 40 for i in range(num_players)}
    players_time = {request.form[f'player{i+1}']: 0 for i in range(num_players)}
    players_decks = {request.form[f'player{i+1}']: request.form[f'deck{i+1}'] for i in range(num_players)}
    players_win = {request.form[f'player{i+1}']: 0 for i in range(num_players)}
    players_start = {request.form[f'player{i+1}']: 0 for i in range(num_players)}
    
    # Get the list of player names from the form inputs
    player_names = [request.form[f'player{i+1}'] for i in range(num_players)]
    deck_names = [request.form[f'deck{i+1}'] for i in range(num_players)]
        
    start_game_radio = (request.form['start_game'])
    digit = 0
    
    for char in start_game_radio:
        if char.isdigit():
            digit = char
            break
    
    # Set Active player to starting player
    active_player_index = int(digit) - 1
    
    # Get the keys (players) as a list and access the nth key
    player_to_change = list(players_start.keys())[active_player_index]

    # Change the value of the nth player to 1
    players_start[player_to_change] = 1

    # Tests
    print(new_game_id)      
    print(players_win)
    print(players_life)
    
    # Update time
    start_time = time.time()
    turn_time = time.time()
    start_turn_time = time.time()
    
    # Elapsed_time
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # Game ID
    folder_path = "data/"
    filename = os.path.join(folder_path, "game_data.csv")
    last_game_id = read_last_game_id(filename)
    
    return render_template('index.html', players=players_life, active_player=list(players_life.keys())[active_player_index], turn_count=turn_count, elapsed_time=elapsed_time,
                           turn_time=turn_time, players_time=players_time, player_names=player_names, active_player_index=active_player_index, deck_names=deck_names, 
                           players_win= players_win, players_start=players_start, last_game_id = last_game_id)
    
@app.route('/update_life', methods=['POST'])
def update_life():
    global players_life, start_time, players_time, deck_names
    player = request.form['player']
    action = request.form['action']
    amount = int(request.form['amount'])

    if action == 'increase':
        players_life[player] += amount
    elif action == 'decrease':
        players_life[player] -= amount
   
    print(players_start)      
    print(players_win)
    print(players_life)     

    #  Elapsed_time
    end_time = time.time()
    elapsed_time = end_time - start_time

    return render_template('index.html', players=players_life, active_player=list(players_life.keys())[active_player_index], 
                           turn_count=turn_count,  elapsed_time=elapsed_time, players_time = players_time, 
                           active_player_index = active_player_index, deck_names = deck_names, start_time = start_time, players_start = players_start)

@app.route('/pass_turn', methods=['POST'])
def pass_turn():
    global active_player_index, turn_count, start_time, start_turn_time, turn_time, elapsed_time, players_time, active_player_index, deck_names 
    
    end_time = time.time()
    turn_time = end_time - start_turn_time
    
    # Update players' turn times
    active_player = list(players_life.keys())[active_player_index]
    players_time[active_player] = players_time.get(active_player, 0) + turn_time
    
    # Update active player index
    active_player_index = (active_player_index + 1) % len(players_life)
    
    if active_player_index == 0:  # If it's the first player's turn again
        turn_count += 1

     # Start time for the next turn
    start_turn_time = time.time() 
 
    #  Elapsed_time
    elapsed_time = end_time - start_time
    
    return render_template('index.html', players=players_life, active_player=list(players_life.keys())[active_player_index], 
                           turn_count=turn_count, start_turn_time = start_turn_time, elapsed_time=elapsed_time, 
                           turn_time = turn_time, players_time = players_time, active_player_index = active_player_index,
                           deck_names = deck_names, start_time = start_time, players_start = players_start)

@app.route('/change_active_player', methods=['POST'])
def change_active_player():
    global active_player_index, start_time, elapsed_time, players_time, deck_names, start_turn_time
    
    
    # Update players' turn times
    end_time = time.time()
    turn_time = end_time - start_turn_time
    
    #  Elapsed_time
    elapsed_time = end_time - start_time
    
    active_player = list(players_life.keys())[active_player_index]
    players_time[active_player] = players_time.get(active_player, 0) + turn_time
    
    selected_player = request.form.get('active_player')  # Get the selected player from the form data
    active_player_index = list(players_life.keys()).index(selected_player)  # Set active player index based on selected player
    
    # Start time for the next turn
    start_turn_time = time.time()
    
    return render_template('index.html', players=players_life, active_player=selected_player, turn_count=turn_count,start_turn_time = start_turn_time,
                           elapsed_time=elapsed_time, active_player_index = active_player_index, players_time = players_time, deck_names = deck_names, start_time = start_time, 
                           players_start = players_start)


@app.route('/end_game', methods=['POST'])
def render_end():
    
    
    return render_template('game_over.html', players_win=players_win, players=players_life, active_player=list(players_life.keys())[active_player_index],
                           turn_count=turn_count, start_turn_time = start_turn_time, turn_time = turn_time, players_time = players_time, active_player_index = active_player_index,
                           deck_names = deck_names, start_time = start_time, players_start = players_start)

@app.route('/update_winner', methods=['POST'])
def update_winner():
    global players_win, active_player_index, turn_count, start_time, start_turn_time, turn_time, elapsed_time, players_time, active_player_index, deck_names, players_start
    player_won_select = None
    
    # Reset all players' win counts to 0
    for player in players_win:
        players_win[player] = 0
    
    # Get the selected winner from the form data
    player = request.form['winner']
    
    # Increment the win count for the selected winner
    players_win[player] += 1
    
    # Render the template with updated data
    return render_template('game_over.html', players_win=players_win, players=players_life, active_player=list(players_life.keys())[active_player_index],
                           turn_count=turn_count, start_turn_time = start_turn_time, turn_time = turn_time, players_time = players_time, active_player_index = active_player_index,
                           deck_names = deck_names, start_time = start_time, players_start = players_start, player_won_select = players_win[player])


@app.route('/export_csv', methods=['POST'])
def export_csv():
    # Data
    data = [[
            'Game_ID',
            'Game_Type',
            'Date',
            'Player', 
            'Commander',
            'Start',
            'Life', 
            'Time (Minutes)',
            'Win Turn',
            'Win',
            ]]
    for player in players_life:
        data.append([
            last_game_id + 1,
            "Normal",
            datetime.now().strftime('%d-%m-%Y'),
            player, 
            players_decks[player],
            players_start[player],
            players_life[player],  
            round(players_time[player] / 60, 2), 
            turn_count,
            players_win[player]])

    # Save copy to server
    save_csv(data)  # Save CSV data to a file on the server
     
   # Return JSON response along with the CSV file as an attachment
    return render_template('game_over.html', players_win=players_win, players=players_life, active_player=list(players_life.keys())[active_player_index],
                           turn_count=turn_count, start_turn_time = start_turn_time, turn_time = turn_time, players_time = players_time, active_player_index = active_player_index,
                           deck_names = deck_names, start_time = start_time, players_start = players_start)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
