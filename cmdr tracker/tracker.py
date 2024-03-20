from flask import Flask, render_template, request, Response
import time
import csv
from io import StringIO

app = Flask(__name__)

# Initate players
players_life = {'Player 1': 40, 'Player 2': 40, 'Player 3': 40, 'Player 4': 40}
players_time = {'Player 1': 0, 'Player 2': 0, 'Player 3': 0, 'Player 4': 0}
players_decks = {'Player 1': "Default1", 'Player 2': "Default1", 'Player 3': "Default1", 'Player 4': "Default1"}
players_win = {'Player 1': 0, 'Player 2': 0, 'Player 3': 0, 'Player 4': 0}

# Initial active player, turn count, start_time, turn_time, start_turn_time
active_player_index = 0
turn_count = 1
start_time = None
turn_time = None
start_turn_time = None

# Load suggestions
def read_txt_file(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    return [line.strip() for line in lines]


@app.route('/')
def index():
    global active_player_index, turn_count
    
    active_player_index = 0
    turn_count = 1
    
    player_names_suggestions = read_txt_file('player_names.txt')  
    commander_names_suggestions = read_txt_file('commander_names.txt')    

    return render_template('enter_players.html', commander_names_suggestions = commander_names_suggestions, player_names_suggestions = player_names_suggestions, 
                           active_player_index = active_player_index, turn_count = turn_count)

@app.route('/submit_players', methods=['POST'])
def submit_players():
    global players_life, start_time, turn_time, start_turn_time, player_names, active_player_index, players_time, deck_names, players_decks, players_win
    
    num_players = int(request.form['num_players'])
    players_life = {request.form[f'player{i+1}']: 40 for i in range(num_players)}
    players_time = {request.form[f'player{i+1}']: 0 for i in range(num_players)}
    players_decks = {request.form[f'player{i+1}']: request.form[f'deck{i+1}'] for i in range(num_players)}
    players_win = {request.form[f'player{i+1}']: 0 for i in range(num_players)}

    
    # Get the list of player names from the form inputs
    player_names = [request.form[f'player{i+1}'] for i in range(num_players)]
    deck_names = [request.form[f'deck{i+1}'] for i in range(num_players)]
  
    
    print(players_time)
    print(players_decks)
    print(players_win)
    
    # Update time
    start_time = time.time()
    turn_time = time.time()
    start_turn_time = time.time()
    
    # Elapsed_time
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    return render_template('index.html', players=players_life, active_player=list(players_life.keys())[active_player_index], turn_count=turn_count, elapsed_time=elapsed_time,
                           turn_time=turn_time, players_time=players_time, player_names=player_names, active_player_index=active_player_index, deck_names=deck_names, players_win= players_win)
    
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

    #  Elapsed_time
    end_time = time.time()
    elapsed_time = end_time - start_time

    return render_template('index.html', players=players_life, active_player=list(players_life.keys())[active_player_index], 
                           turn_count=turn_count,  elapsed_time=elapsed_time, players_time = players_time, 
                           active_player_index = active_player_index, deck_names = deck_names)

@app.route('/pass_turn', methods=['POST'])
def pass_turn():
    global active_player_index, turn_count, start_time, start_turn_time, turn_time, elapsed_time, players_time, active_player_index, deck_names
    
    end_time = time.time()
    turn_time = end_time - start_turn_time
    
    # Update players' turn times
    active_player = list(players_life.keys())[active_player_index]
    players_time[active_player] = players_time.get(active_player, 0) + turn_time
    print(players_time)
    print(players_life)
    
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
                           deck_names = deck_names)

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
                           elapsed_time=elapsed_time, active_player_index = active_player_index, players_time = players_time, deck_names = deck_names)


@app.route('/update_winner', methods=['POST'])
def update_winner():
    global players_win, active_player_index, turn_count, start_time, start_turn_time, turn_time, elapsed_time, players_time, active_player_index, deck_names
    
    # Reset all players' win counts to 0
    for player in players_win:
        players_win[player] = 0
    
    # Get the selected winner from the form data
    player = request.form['winner']
    
    # Increment the win count for the selected winner
    players_win[player] += 1
    
    # Render the template with updated data
    return render_template('index.html', players_win=players_win, players=players_life, active_player=list(players_life.keys())[active_player_index],
                           turn_count=turn_count, start_turn_time = start_turn_time, turn_time = turn_time, players_time = players_time, active_player_index = active_player_index,
                           deck_names = deck_names)

   
@app.route('/export_csv', methods=['POST'])
def export_csv():
    # Data
    data = [[
            'Game_ID',
            'Game_Type'
            'Date',
            'Player', 
            'Commander',
            'Start',
            'Life', 
            'Time (Minutes)',
            'Win'
            'Win Turn',
            ]]
    
    for player in players_life:
        data.append([
            0,
            0,
            0,
            player, 
            players_decks[player],
            0,
            players_life[player],  
            round(players_time[player] / 60, 2), 
            turn_count,
            players_win[player]])

    # Create a CSV string
    output = StringIO()
    writer = csv.writer(output)
    writer.writerows(data)

    # Prepare response
    output.seek(0)
    return Response(output, mimetype='text/csv', headers={'Content-Disposition': 'attachment;filename=data.csv'})

if __name__ == '__main__':
    app.run(debug=True)
