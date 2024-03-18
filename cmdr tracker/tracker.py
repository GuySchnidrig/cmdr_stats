from flask import Flask, render_template, request, jsonify
import time
import pandas as pd

app = Flask(__name__)

# Initial life totals for 4 players
players_life = {'Player 1': 40, 'Player 2': 40, 'Player 3': 40, 'Player 4': 40}

# Initial active player and turn count
active_player_index = 0
turn_count = 1
start_time = None
turn_time = None
start_turn_time = None


@app.route('/')
def index():
    active_player = list(players_life.keys())[active_player_index]
    return render_template('enter_players.html')

@app.route('/submit_players', methods=['POST'])
def submit_players():
    global players_life, start_time, turn_time, start_turn_time, turn_times_df, player_names, active_player_index
    num_players = int(request.form['num_players'])
    players_life = {request.form[f'player{i+1}']: 40 for i in range(num_players)}
    
    # Get the list of player names from the form inputs
    player_names = [request.form[f'player{i+1}'] for i in range(num_players)]
    
    # Create a pandas DataFrame to store turn times per player
    turn_times_df = pd.DataFrame(0, index=[0], columns=[active_player_index])
    
    # time
    start_time = time.time()
    turn_time = time.time()
    start_turn_time = time.time()
    end_time = time.time()
    elapsed_time = end_time - start_time
    return render_template('index.html', players=players_life, active_player=list(players_life.keys())[active_player_index], turn_count=turn_count, elapsed_time=elapsed_time, turn_time=turn_time, turn_times_df = turn_times_df, player_names = player_names, active_player_index = active_player_index)

@app.route('/update_life', methods=['POST'])
def update_life():
    global players_life, start_time, turn_times_df
    player = request.form['player']
    action = request.form['action']
    amount = int(request.form['amount'])

    if action == 'increase':
        players_life[player] += amount
    elif action == 'decrease':
        players_life[player] -= amount

    end_time = time.time()
    elapsed_time = end_time - start_time

    return render_template('index.html', players=players_life, active_player=list(players_life.keys())[active_player_index], turn_count=turn_count,  elapsed_time=elapsed_time, turn_times_df = turn_times_df, active_player_index = active_player_index)

@app.route('/pass_turn', methods=['POST'])
def pass_turn():
    global active_player_index, turn_count, start_time, start_turn_time, turn_time, elapsed_time, turn_times_df, active_player_index
    active_player_index = (active_player_index + 1) % len(players_life)
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    turn_time = end_time - start_turn_time
    
    # Append turn time for the active player to the DataFrame
    turn_times_df[active_player_index] = [turn_time]
    print(turn_times_df)

    if active_player_index == 0:  # If it's the first player's turn again
        turn_count += 1

    start_turn_time = time.time()  # Start time for the next turn

    return render_template('index.html', players=players_life, active_player=list(players_life.keys())[active_player_index], turn_count=turn_count, start_turn_time = start_turn_time, elapsed_time=elapsed_time, 
                           turn_time = turn_time, turn_times_df = turn_times_df, active_player_index = active_player_index)


@app.route('/change_active_player', methods=['POST'])
def change_active_player():
    global active_player_index, start_time, elapsed_time
    selected_player = request.form.get('active_player')  # Get the selected player from the form data
    active_player_index = list(players_life.keys()).index(selected_player)  # Set active player index based on selected player
    end_time = time.time()
    elapsed_time = end_time - start_time
    return render_template('index.html', players=players_life, active_player=selected_player, turn_count=turn_count,  elapsed_time=elapsed_time, active_player_index = active_player_index)

if __name__ == '__main__':
    app.run(debug=True)
