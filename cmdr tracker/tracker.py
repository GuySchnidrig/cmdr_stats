from flask import Flask, render_template, request, jsonify
import time

app = Flask(__name__)

# Initial life totals for 4 players
players_life = {'Player 1': 40, 'Player 2': 40, 'Player 3': 40, 'Player 4': 40}

# Initial active player and turn count
active_player_index = 0
turn_count = 1

@app.route('/')
def index():
    active_player = list(players_life.keys())[active_player_index]
    return render_template('enter_players.html')

@app.route('/submit_players', methods=['POST'])
def submit_players():
    global players_life
    num_players = int(request.form['num_players'])
    players_life = {request.form[f'player{i+1}']: 40 for i in range(num_players)}
    return render_template('index.html', players=players_life, active_player=list(players_life.keys())[active_player_index], turn_count=turn_count, start_time = time.time())

@app.route('/update_life', methods=['POST'])
def update_life():
    global players_life
    player = request.form['player']
    action = request.form['action']
    amount = int(request.form['amount'])

    if action == 'increase':
        players_life[player] += amount
    elif action == 'decrease':
        players_life[player] -= amount

    return render_template('index.html', players=players_life, active_player=list(players_life.keys())[active_player_index], turn_count=turn_count)

@app.route('/pass_turn', methods=['POST'])
def pass_turn():
    global active_player_index, turn_count
    active_player_index = (active_player_index + 1) % len(players_life)
    if active_player_index == 0:  # If it's the first player's turn again
        turn_count += 1
    return render_template('index.html', players=players_life, active_player=list(players_life.keys())[active_player_index], turn_count=turn_count)

@app.route('/change_active_player', methods=['POST'])
def change_active_player():
    global active_player_index
    selected_player = request.form.get('active_player')  # Get the selected player from the form data
    active_player_index = list(players_life.keys()).index(selected_player)  # Set active player index based on selected player
    return render_template('index.html', players=players_life, active_player=selected_player, turn_count=turn_count)

if __name__ == '__main__':
    app.run(debug=True)
