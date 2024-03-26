# Import libraries
from flask import Flask, render_template, request, Response, jsonify, redirect, url_for, session, flash
import time
import csv
from io import StringIO
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Get the directory of the currently executing script
script_directory = os.path.dirname(__file__)

# Set the current working directory to the script directory
os.chdir(script_directory)

# Configuration settings
USER_CREDENTIALS = {'username': 'Guy', 'password': '1234'}

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
 
 # Function to read CSV and define last game id
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

player_names_suggestions = read_txt_file('player_names.txt')  
commander_names_suggestions = read_txt_file('legends.txt')

@app.route('/')
def index():
    if 'logged_in' in session and session['logged_in']:
        return(redirect(url_for('login')))
    else:
        return(redirect(url_for('login')))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == USER_CREDENTIALS['username'] and password == USER_CREDENTIALS['password']:
            session['logged_in'] = True
            session['username'] = username
            flash("Login successful!", "success")
            return redirect(url_for('enter_players'))
        else:
            flash("Invalid username or password. Please try again.", "error")
    return render_template('login.html')


@app.route('/enter_players')
def enter_players():
    if 'logged_in' in session and session['logged_in']:
        session['players_life'] = {'Player 1': 40, 'Player 2': 40, 'Player 3': 40, 'Player 4': 40}
        session['players_time'] = {'Player 1': 0, 'Player 2': 0, 'Player 3': 0, 'Player 4': 0}
        session['players_decks'] = {'Player 1': "Default1", 'Player 2': "Default1", 'Player 3': "Default1", 'Player 4': "Default1"}
        session['players_win'] = {'Player 1': 0, 'Player 2': 0, 'Player 3': 0, 'Player 4': 0}
        session['players_start'] = {'Player 1': 0, 'Player 2': 0, 'Player 3': 0, 'Player 4': 0}

        session['active_player_index'] = 0
        session['turn_count'] = 1
        session['start_time'] = None
        session['turn_time'] = None
        session['start_turn_time'] = None
        session['new_game_id'] = 0
        session['num_players'] = 0
        
    return render_template('enter_players.html', 
                           commander_names_suggestions=commander_names_suggestions,
                           player_names_suggestions=player_names_suggestions)


@app.route('/submit_test', methods=['POST'])
def submit_test():
    session['num_players'] = int(request.form['num_players'])
    session['players_life'] = {request.form[f'player{i+1}']: 40 for i in range(session['num_players'])}
    session['players_time'] = {request.form[f'player{i+1}']: 0 for i in range(session['num_players'])}
    session['players_decks'] = {request.form[f'player{i+1}']: request.form[f'deck{i+1}'] for i in range(session['num_players'])}
    session['players_win'] = {request.form[f'player{i+1}']: 0 for i in range(session['num_players'])}
    session['players_start'] = {request.form[f'player{i+1}']: 0 for i in range(session['num_players'])}
    session['player_names'] = [request.form[f'player{i+1}'] for i in range(session['num_players'])]
    session['deck_names'] = [request.form[f'deck{i+1}'] for i in range(session['num_players'])]
    session['turn_count'] = 1
    
    start_game_radio = (request.form['start_game'])
    digit = 0
    
    for char in start_game_radio:
        if char.isdigit():
            digit = char
            break

    # Set Active player to starting player
    session['active_player_index'] = int(digit) - 1

    # Get the keys (players) as a list and access the nth key
    player_to_change = list(session['players_start'].keys())[session['active_player_index']]

    # Change the value of the nth player to 1
    session['players_start'][player_to_change] = 1

    # Update time
    session['start_time'] = time.time()
    session['turn_time'] = time.time()
    session['start_turn_time'] = time.time()
    
    # Elapsed_time
    session['end_time'] = time.time()
    session['elapsed_time'] = session['end_time'] - session['start_time'] 
    
    # Game ID
    folder_path = "data/"
    filename = os.path.join(folder_path, "game_data.csv")
    session['last_game_id'] = read_last_game_id(filename)

    return render_template('index.html',
                           players  = session['players_life'],
                           players_life = session['players_life'],
                           players_time = session['players_time'],
                           players_decks = session['players_decks'],
                           players_win = session['players_win'],
                           players_start = session['players_start'],
                           player_names = session['player_names'],
                           active_player_index = session['active_player_index'],
                           turn_count = session['turn_count'],
                           elapsed_time = session['elapsed_time'],
                           turn_time = session['turn_time'],
                           deck_names = session['deck_names'],
                           last_game_id = session['last_game_id'])


@app.route('/update_life', methods=['POST'])
def update_life():
    player = request.form['player']
    action = request.form['action']
    amount = int(request.form['amount'])

    if action == 'increase':
        players_life[player] += amount
    elif action == 'decrease':
        players_life[player] -= amount

    #  Elapsed_time
    end_time = time.time()
    elapsed_time = end_time - start_time

    return render_template('index.html', players=players_life, active_player=list(players_life.keys())[active_player_index], 
                           turn_count=turn_count,  elapsed_time=elapsed_time, players_time = players_time, digit = digit,
                           active_player_index = active_player_index, deck_names = deck_names, start_time = start_time, players_start = players_start)

@app.route('/pass_turn', methods=['POST'])
def pass_turn():
    global active_player_index, turn_count, start_time, start_turn_time, turn_time, elapsed_time, players_time, active_player_index, deck_names, digit
    
    end_time = time.time()
    turn_time = end_time - start_turn_time
    
    # Update players' turn times
    active_player = list(players_life.keys())[active_player_index]
    players_time[active_player] = players_time.get(active_player, 0) + turn_time
    
    # Update active player index
    active_player_index = (active_player_index - 1) % len(players_life)
    
    if active_player_index == (int(digit) - 1):  # If it's the first player's turn again
        turn_count += 1

     # Start time for the next turn
    start_turn_time = time.time() 
 
    #  Elapsed_time
    elapsed_time = end_time - start_time
    
    return render_template('index.html', players=players_life, active_player=list(players_life.keys())[active_player_index], 
                           turn_count=turn_count, start_turn_time = start_turn_time, elapsed_time=elapsed_time, 
                           turn_time = turn_time, players_time = players_time, active_player_index = active_player_index,
                           deck_names = deck_names, start_time = start_time, players_start = players_start, digit = digit)

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
                           players_start = players_start, digit = digit)


@app.route('/end_game', methods=['POST'])
def render_end():
    
    
    return render_template('game_over.html', players_win=players_win, players=players_life, active_player=list(players_life.keys())[active_player_index],
                           turn_count=turn_count, start_turn_time = start_turn_time, turn_time = turn_time, players_time = players_time, active_player_index = active_player_index,
                           deck_names = deck_names, start_time = start_time, players_start = players_start, digit = digit)

@app.route('/update_winner', methods=['POST'])
def update_winner():
    global players_win, active_player_index, turn_count, start_time, start_turn_time, turn_time, elapsed_time, players_time, active_player_index, deck_names, players_start, win_type, mv_card
    

    # Reset all players' win counts to 0
    for player in players_win:
        players_win[player] = 0
    
    # Get the selected winner from the form data
    player = request.form['winner']
    
    # Increment the win count for the selected winner
    players_win[player] += 1
    
    # Get the selected gameWinningType
    win_type = request.form['gameWinningType']
    
    mv_card = request.form['mvpCard']
    
    # Render the template with updated data
    return render_template('game_over.html', players_win=players_win, players=players_life, active_player=list(players_life.keys())[active_player_index],
                           turn_count=turn_count, start_turn_time = start_turn_time, turn_time = turn_time, players_time = players_time, active_player_index = active_player_index,
                           deck_names = deck_names, start_time = start_time, players_start = players_start, player_won_select = players_win[player], digit = digit, win_type = win_type, mv_card = mv_card)


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
            'Win',
            'Win_Turn',
            'Win_Type',
            'mv_card',
            'Life', 
            'Time (Minutes)',
            'Deck_Link' 
            ]]
    for player in players_life:
        data.append([
            last_game_id + 1,                          # Game ID
            "Normal",                                  # Game Type
            datetime.now().strftime('%d-%m-%Y'),       # Date
            player,                                    # Player
            players_decks[player],                     # Commander
            players_start[player],                     # Start
            players_win[player],                       # Win
            turn_count,                                # Win Turn
            win_type,                                  # Win Type
            mv_card,                                   # mv_card
            players_life[player],                      # Life
            round(players_time[player] / 60, 2),       # Time  
            None                                       # Space for Deck link
            ])      
                                                         

    # Save copy to server
    save_csv(data)  # Save CSV data to a file on the server
     
   # Return JSON response along with the CSV file as an attachment
    return render_template('game_over.html', players_win=players_win, players=players_life, active_player=list(players_life.keys())[active_player_index],
                           turn_count=turn_count, start_turn_time = start_turn_time, turn_time = turn_time, players_time = players_time, active_player_index = active_player_index,
                           deck_names = deck_names, start_time = start_time, players_start = players_start, digit = digit)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')