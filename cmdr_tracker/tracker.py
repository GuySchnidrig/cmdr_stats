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
USER_CREDENTIALS = {
    'Aless': '1234',
    'Domi': '1234',
    'Domi69': '1234',
    'Elie': '1234',
    'Fubu': '1234',
    'Guy': '1234',
    'Lucien': '1234',
    'Lueku': '1234',
    'Nico': '1234',
    'Nils': '1234',
    'Tobi': '1234',
    'Vince': '1234'
}

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
        if username in USER_CREDENTIALS and password == USER_CREDENTIALS[username]:
            session['logged_in'] = True
            session['username'] = username
            flash("Login successful!", "info")
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
    print(session)    
    return render_template('enter_players.html', 
                           commander_names_suggestions=commander_names_suggestions,
                           player_names_suggestions=player_names_suggestions)


@app.route('/submit_test', methods=['GET', 'POST'] )
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
    session['digit'] = 0
    
    for char in start_game_radio:
        if char.isdigit():
            session['digit'] = char
            break

    # Set Active player to starting player
    session['active_player_index'] = int(session['digit']) - 1

    # Get the keys (players) as a list and access the nth key
    player_to_change = list(session['players_start'].keys())[session['active_player_index']]

    # Change the value of the nth player to 1
    session['players_start'][player_to_change] = 1

    # Update time
    session['start_time'] = time.time()
    session['turn_time'] = time.time()
    session['start_turn_time'] = time.time()
    
    # Elapsed_time
    end_time = time.time()
    session['elapsed_time'] = end_time - session['start_time'] 
    
    # Game ID
    folder_path = "data/"
    filename = os.path.join(folder_path, "game_data.csv")
    session['last_game_id'] = read_last_game_id(filename)
    print(session)
    return render_template('index.html',
                           players  = session['players_life'],
                           players_life = session['players_life'],
                           players_time = session['players_time'],
                           players_decks = session['players_decks'],
                           players_win = session['players_win'],
                           players_start = session['players_start'],
                           player_names = session['player_names'],
                           active_player_index = session['active_player_index'],
                           active_player = list(session['players_life'].keys())[session['active_player_index']],
                           turn_count = session['turn_count'],
                           turn_time = session['turn_time'],
                           deck_names = session['deck_names'],
                           last_game_id = session['last_game_id'],
                           digit = session['digit'],
                           elapsed_time = session['elapsed_time'],
                           start_time = session['start_time'],
                           start_turn_time = session['start_turn_time']
                           )


@app.route('/update_life', methods=['POST'])
def update_life():
    session['player'] = request.form['player']
    session['action'] = request.form['action']
    session['amount'] = int(request.form['amount'])

    if session['action'] == 'increase':
         session['players_life'][session['player']] += session['amount']
    elif session['action'] == 'decrease':
         session['players_life'][session['player']] -= session['amount']

    #  Elapsed_time
    end_time = time.time()
    session['elapsed_time'] = end_time - session['start_time']

    return render_template('index.html',
                           players  = session['players_life'],
                           players_life = session['players_life'],
                           players_time = session['players_time'],
                           players_decks = session['players_decks'],
                           players_win = session['players_win'],
                           players_start = session['players_start'],
                           player_names = session['player_names'],
                           active_player_index = session['active_player_index'],
                           active_player = list(session['players_life'].keys())[session['active_player_index']],
                           turn_count = session['turn_count'],
                           turn_time = session['turn_time'],
                           deck_names = session['deck_names'],
                           last_game_id = session['last_game_id'],
                           digit = session['digit'],
                           elapsed_time = session['elapsed_time'],
                           start_time = session['start_time'],
                           start_turn_time = session['start_turn_time'])
    


@app.route('/pass_turn', methods=['POST'])
def pass_turn():
    
    end_time = time.time()
    turn_time = end_time - session['start_turn_time']
    
    # Update players' turn times
    active_player = list(session['players_life'].keys())[session['active_player_index']]
    session['players_time'][active_player] =  session['players_time'].get(active_player, 0) + turn_time
    
    # Update active player index
    session['active_player_index'] = (session['active_player_index'] + 1) % len(session['players_life'])
    
    if session['active_player_index'] == (int(session['digit']) - 1):  # If it's the first player's turn again
         session['turn_count'] += 1

     # Start time for the next turn
    session['start_turn_time'] = time.time() 
 
    #  Elapsed_time
    session['elapsed_time'] = end_time - session['start_time']
    
    return render_template('index.html',
                          players  = session['players_life'],
                           players_life = session['players_life'],
                           players_time = session['players_time'],
                           players_decks = session['players_decks'],
                           players_win = session['players_win'],
                           players_start = session['players_start'],
                           player_names = session['player_names'],
                           active_player_index = session['active_player_index'],
                           active_player = list(session['players_life'].keys())[session['active_player_index']],
                           turn_count = session['turn_count'],
                           turn_time = session['turn_time'],
                           deck_names = session['deck_names'],
                           last_game_id = session['last_game_id'],
                           digit = session['digit'],
                           elapsed_time = session['elapsed_time'],
                           start_time = session['start_time'],
                           start_turn_time = session['start_turn_time'])

@app.route('/change_active_player', methods=['POST'])
def change_active_player():
  
    # Update players' turn times
    end_time = time.time()
    turn_time = end_time - session['start_turn_time']
    
    #  Elapsed_time
    session['elapsed_time'] = end_time -  session['start_time']
    
    active_player = list(session['players_life'].keys())[session['active_player_index']]
    session['players_time'][active_player] = session['players_time'].get(active_player, 0) + turn_time
    
    selected_player = request.form.get('active_player')  # Get the selected player from the form data
    session['active_player_index'] = list(session['players_life'].keys()).index(selected_player)  # Set active player index based on selected player
    
    # Start time for the next turn
    session['start_turn_time'] = time.time()
    
    return render_template('index.html',
                         players  = session['players_life'],
                           players_life = session['players_life'],
                           players_time = session['players_time'],
                           players_decks = session['players_decks'],
                           players_win = session['players_win'],
                           players_start = session['players_start'],
                           player_names = session['player_names'],
                           active_player_index = session['active_player_index'],
                           active_player = list(session['players_life'].keys())[session['active_player_index']],
                           turn_count = session['turn_count'],
                           turn_time = session['turn_time'],
                           deck_names = session['deck_names'],
                           last_game_id = session['last_game_id'],
                           digit = session['digit'],
                           elapsed_time = session['elapsed_time'],
                           start_time = session['start_time'],
                           start_turn_time = session['start_turn_time'])


@app.route('/end_game', methods=['POST'])
def render_end():
    
    
    return render_template('game_over.html',
                           players  = session['players_life'],
                           players_life = session['players_life'],
                           players_time = session['players_time'],
                           players_decks = session['players_decks'],
                           players_win = session['players_win'],
                           players_start = session['players_start'],
                           player_names = session['player_names'],
                           active_player_index = session['active_player_index'],
                           active_player = list(session['players_life'].keys())[session['active_player_index']],
                           turn_count = session['turn_count'],
                           turn_time = session['turn_time'],
                           deck_names = session['deck_names'],
                           last_game_id = session['last_game_id'],
                           digit = session['digit'],
                           elapsed_time = session['elapsed_time'],
                           start_time = session['start_time'],
                           start_turn_time = session['start_turn_time'])

@app.route('/update_winner', methods=['POST'])
def update_winner():

    # Get the selected winner from the form data
    player = request.form['winner']
    
        # Reset all players' win counts to 0
    for player in session['players_win']:
        session['players_win'][player] = 0
    
    # Increment the win count for the selected winner
    session['players_win'][player] += 1
    
    # Get the selected gameWinningType
    session['win_type'] = request.form['gameWinningType']
    
    session['mv_card'] = request.form['mvpCard']
    
    # Render the template with updated data
    return render_template('game_over.html', 
                           players  = session['players_life'],
                           players_life = session['players_life'],
                           players_time = session['players_time'],
                           players_decks = session['players_decks'],
                           players_win = session['players_win'],
                           players_start = session['players_start'],
                           player_names = session['player_names'],
                           active_player_index = session['active_player_index'],
                           active_player = list(session['players_life'].keys())[session['active_player_index']],
                           turn_count = session['turn_count'],
                           turn_time = session['turn_time'],
                           deck_names = session['deck_names'],
                           last_game_id = session['last_game_id'],
                           elapsed_time = session['elapsed_time'],
                           start_time = session['start_time'],
                           start_turn_time = session['start_turn_time'],
                           player_won_select = session['players_win'][player],
                           digit = session['digit'],
                           win_type = session['win_type'],
                           mv_card = session['mv_card'])


@app.route('/export_csv', methods=['POST'])
def export_csv():
    
    game_type = "Normal"
    if session['num_players'] == 3:
        game_type = "Reduced"
    
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
            'Uploader'
            ]]
    for player in session['players_life']:
        data.append([
    session['last_game_id'] + 1,                            # Game ID
            game_type,                                      # Game Type
            datetime.now().strftime('%d-%m-%Y'),            # Date
            player,                                         # Player
            session['players_decks'][player],               # Commander
            session['players_start'][player],               # Start
            session['players_win'][player],                 # Win
            session['turn_count'] ,                         # Win Turn
            session['win_type'],                            # Win Type
            session['mv_card'],                             # mv_card
            session['players_life'][player],                # Life
            round(session['players_time'][player] / 60, 2), # Time  
            None,                                           # Space for Deck link
            session['username']                             # Uploader
            ])      
                                                         

    # Save copy to server
    save_csv(data)  # Save CSV data to a file on the server
     
   # Return JSON response along with the CSV file as an attachment
    return render_template('game_over.html', 
                           players  = session['players_life'],
                           players_life = session['players_life'],
                           players_time = session['players_time'],
                           players_decks = session['players_decks'],
                           players_win = session['players_win'],
                           players_start = session['players_start'],
                           player_names = session['player_names'],
                           active_player_index = session['active_player_index'],
                           active_player = list(session['players_life'].keys())[session['active_player_index']],
                           turn_count = session['turn_count'],
                           turn_time = session['turn_time'],
                           deck_names = session['deck_names'],
                           last_game_id = session['last_game_id'],
                           elapsed_time = session['elapsed_time'],
                           start_time = session['start_time'],
                           start_turn_time = session['start_turn_time'],
                           player_won_select = session['players_win'][player],
                           digit = session['digit'],
                           win_type = session['win_type'],
                           mv_card = session['mv_card'])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')