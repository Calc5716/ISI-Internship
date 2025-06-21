import random
import mysql.connector

# Connecting to MySQL
try:
    my_con = mysql.connector.connect(host="localhost", user="root", passwd="1234", database="ludo_mixed")
    if my_con.is_connected():
        cur = my_con.cursor()
        print("Connected to MySQL database")
except mysql.connector.Error as err:
    print(f"Error connecting to MySQL: {err}")
    my_con = None

# Number of simulations
simul = 10000

# Datapoints needed for analysis
squares = 7  # Number of squares per side
pieces = 2  # The number of tokens per player
max_moves_per_player = 36  # Maximum moves per player

# Player tokens
player_positions = {
    'player1': [0 for _ in range(pieces)],
    'player2': [0 for _ in range(pieces)]
}

# Counting captures
capture_count = {
    'player1': 0,
    'player2': 0
}

# Counting moves
move_count = {
    'player1': 0,
    'player2': 0
}

# Home Score for each token
HOME_SCORE = 29

# Safe scores only for 13squares per side, will change for each type
safe_scores = [0, 14, 27, 28, 29]

# Mapping scores so that we can kill
kill_scores = {
    15: 1, 16: 2, 17: 3, 18: 4, 19: 5, 20: 6,
    21: 7, 22: 8, 23: 9, 24: 10, 25: 11, 26: 12,
    1: 15, 2: 16, 3: 17, 4: 18, 5: 19, 6: 20, 7: 21,
    8: 22, 9: 23, 10: 24, 11: 25, 12: 26
    }

# Mixed bot probabilities
a = random.random()  # probability of choosing aggressive mode
b = 1 - a  # probability of choosing responsible mode


def mixed(alpha, beta):

    modes = ['aggressive', 'responsible-pair']
    selected_mode = random.choices(modes, [alpha, beta], k=1)[0]
    return selected_mode


# Dice rolling function
def dice_roll():
    return [random.randint(1, 6) for _ in range(3)]


# Function to determine whether a piece is safe or not
def is_safe(pos, player):
    return pos in safe_scores or player_positions[player].count(pos) > 1


# Function to capture a token
def capture_tks(new_score, player):
    opponent = 'player2' if player == 'player1' else 'player1'
    captured = False
    mapped_score = kill_scores.get(new_score)

    if mapped_score is not None:
        for i in range(pieces):
            opp_score = player_positions[opponent][i]
            if mapped_score == opp_score and not is_safe(opp_score, opponent):
                player_positions[opponent][i] = 0
                capture_count[player] += 1
                captured = True
                break

    return captured


# Function to update scores
def update_score(player, token_id, dice_val):
    current_score = player_positions[player][token_id]

    if current_score == HOME_SCORE:
        return current_score, False

    new_score = current_score + dice_val

    if new_score >= HOME_SCORE:
        player_positions[player][token_id] = HOME_SCORE
        return HOME_SCORE, True

    player_positions[player][token_id] = new_score
    return new_score, False


def player1_choose_dice(available_dice):
    return max(available_dice)


def player2_choose_dice(available_dice):
    return max(available_dice)


# Aggressive Bot
def aggressive_mode(dice_val, player):
    extra_turn = False

    # Promoting a token
    for idx, pos in enumerate(player_positions[player]):
        if (0 < pos < HOME_SCORE) and (pos + dice_val >= HOME_SCORE):
            new_score, promoted = update_score(player, idx, dice_val)
            if promoted:
                extra_turn = True
            return extra_turn

    # Capturing an opponent token
    opponent = 'player2' if player == 'player1' else 'player1'
    for idx, pos in enumerate(player_positions[player]):
        if 0 < pos < HOME_SCORE:
            new_pos = pos + dice_val
            mapped_score = kill_scores.get(new_pos)
            if mapped_score in player_positions[opponent]:
                opponent_at_pos = False
                for opp_idx, opp_pos in enumerate(player_positions[opponent]):
                    if opp_pos == mapped_score and not is_safe(mapped_score, opponent):
                        opponent_at_pos = True
                        break

                if opponent_at_pos:
                    new_score, _ = update_score(player, idx, dice_val)
                    captured = capture_tks(new_score, player)
                    if captured:
                        extra_turn = True
                    return extra_turn

    # Moving to safe square
    for idx, pos in enumerate(player_positions[player]):
        if 0 < pos < HOME_SCORE:
            new_pos = pos + dice_val
            if new_pos in safe_scores:
                update_score(player, idx, dice_val)
                return extra_turn

    # Moving first active token
    for idx, pos in enumerate(player_positions[player]):
        if 0 < pos < HOME_SCORE:
            update_score(player, idx, dice_val)
            return extra_turn

    # If no tokens are active then activating one
    for idx, pos in enumerate(player_positions[player]):
        if pos == 0:
            update_score(player, idx, dice_val)
            return extra_turn

    return extra_turn


# Responsible Pair
def responsible_pair_mode(dice_val, player):
    extra_turn = False
    active_tokens = [i for i, pos in enumerate(player_positions[player]) if 0 < pos < HOME_SCORE]
    opponent = 'player2' if player == 'player1' else 'player1'

    # Promoting a token
    for token in active_tokens:
        if player_positions[player][token] + dice_val >= HOME_SCORE:
            new_score, promoted = update_score(player, token, dice_val)
            if promoted:
                extra_turn = True
            return extra_turn

    # Capturing one token
    for token in active_tokens:
        new_pos = player_positions[player][token] + dice_val
        mapped = kill_scores.get(new_pos)
        if mapped in player_positions[opponent]:
            opponent_at_pos = False
            for opp_idx, opp_pos in enumerate(player_positions[opponent]):
                if opp_pos == mapped and not is_safe(mapped, opponent):
                    opponent_at_pos = True
                    break

            if opponent_at_pos:
                new_score, _ = update_score(player, token, dice_val)
                captured = capture_tks(new_score, player)
                if captured:
                    extra_turn = True
                return extra_turn

    # Situational aggressive movement
    if any(pos >= 50 for pos in player_positions[opponent]):
        if active_tokens:
            highest_token = max(active_tokens, key=lambda i: player_positions[player][i])
            update_score(player, highest_token, dice_val)
            return extra_turn

    # Moving to Safe Square
    for token in active_tokens:
        if player_positions[player][token] + dice_val in safe_scores:
            update_score(player, token, dice_val)
            return extra_turn

    # Chasing opponent using last 2 tokens
    if len(active_tokens) >= 2:
        last_two = sorted(active_tokens, key=lambda i: player_positions[player][i])[-2:]
        for token in last_two:
            for opp_pos in player_positions[opponent]:
                if 0 < opp_pos < HOME_SCORE:
                    if abs((player_positions[player][token] + dice_val) - opp_pos) <= 6:
                        update_score(player, token, dice_val)
                        return extra_turn

    # Pair movement before reaching 26
    pair_tokens = [i for i in active_tokens if player_positions[player][i] < 26]
    if len(pair_tokens) >= 2:
        first = min(pair_tokens, key=lambda i: player_positions[player][i])
        update_score(player, first, dice_val)
        return extra_turn

    # Paired movement after all reached 26
    post_26 = [i for i in active_tokens if player_positions[player][i] >= 26]
    if len(post_26) >= 2:
        first = min(post_26, key=lambda i: player_positions[player][i])
        update_score(player, first, dice_val)
        return extra_turn

    # Move first active token or activate new token
    if active_tokens:
        update_score(player, active_tokens[0], dice_val)
        return extra_turn

    # Try to activate a token
    for idx, pos in enumerate(player_positions[player]):
        if pos == 0:
            update_score(player, idx, dice_val)
            return extra_turn

    return extra_turn


# Mixed Bot
def mixed_bot(dice_val):
    strategy = mixed(a, b)  # Chooses moves based on probabilities
    if strategy == 'aggressive':
        return aggressive_mode(dice_val, 'player1')
    else:
        return responsible_pair_mode(dice_val, 'player1')


# Function to check the winner
def check_winner():
    player1_home = sum(1 for pos in player_positions['player1'] if pos == HOME_SCORE)
    player2_home = sum(1 for pos in player_positions['player2'] if pos == HOME_SCORE)

    if player1_home == pieces:
        return 'player1'
    elif player2_home == pieces:
        return 'player2'
    else:
        return None


# Function to determine winner by points if all the pieces does not reach home within the fixed number of moves
def determine_winner_by_points():
    player1_total = sum(player_positions['player1'])
    player2_total = sum(player_positions['player2'])

    if player1_total > player2_total:
        return 'player1'
    elif player2_total > player1_total:
        return 'player2'
    else:
        return 'tie'


# Function to execute a single move by a player
def execute_move(player, dice_value):
    move_count[player] += 1

    if player == 'player1':
        extra_turn = mixed_bot(dice_value)  # Player1 uses mixed bot strategy
    else:
        extra_turn = aggressive_mode(dice_value, 'player2')  # Player2 uses aggressive strategy

    # Check for extra turn due to six or capture
    if dice_value == 6 or extra_turn:
        return True

    return False


# Gameplay function
def play_game():
    global player_positions, capture_count, move_count

    player_positions = {
        'player1': [0 for _ in range(pieces)],
        'player2': [0 for _ in range(pieces)]
    }
    capture_count = {
        'player1': 0,
        'player2': 0
    }
    move_count = {
        'player1': 0,
        'player2': 0
    }

    winner = None
    total_moves = 0
    current_roller = 'player1'

    # will continue until someone wins or exhausts their moves
    while (move_count['player1'] < max_moves_per_player or
           move_count['player2'] < max_moves_per_player) and not winner:

        # Rolling 3 dice
        dice_vals = dice_roll()
        available_dice = dice_vals.copy()

        # Three moves per dice roll cycle
        moves_in_cycle = []

        # Determining the rolling sequence
        if current_roller == 'player1':
            moves_in_cycle = ['player1', 'player2', 'player1']
        else:
            moves_in_cycle = ['player2', 'player1', 'player2']

        extra_turn_earned = False

        for move_num, current_player in enumerate(moves_in_cycle):
            if not available_dice:
                break

            # To check in the player has moves left
            if move_count[current_player] >= max_moves_per_player:
                continue

            # Player chooses dice
            if current_player == 'player1':
                chosen_dice = player1_choose_dice(available_dice)
            else:
                chosen_dice = player2_choose_dice(available_dice)

            available_dice.remove(chosen_dice)

            # Executing move
            earned_extra = execute_move(current_player, chosen_dice)
            if earned_extra:
                extra_turn_earned = True

            total_moves += 1

            # Check for winner after each move
            winner = check_winner()
            if winner:
                break

        # Bonus turns
        if not extra_turn_earned and not winner:
            # Switching roller for next round
            current_roller = 'player2' if current_roller == 'player1' else 'player1'

    # If no winner after all moves are used up then we go by points
    if not winner:
        winner = determine_winner_by_points()

    return total_moves, winner, capture_count['player1'], capture_count['player2']


# Function to create MySQL table
def create_table():
    if my_con and my_con.is_connected():
        try:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS ludo_mixed_vs_responsible_7_2_36 (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    total_moves INT,
                    winner VARCHAR(20),
                    player1_moves_used INT,
                    player2_moves_used INT,
                    player1_final_positions TEXT,
                    player2_final_positions TEXT,
                    player1_captures INT,
                    player2_captures INT,
                    player1_total_points INT,
                    player2_total_points INT,
                    game_completed_early BOOLEAN,
                    mixed_bot_probability FLOAT
                )
            """)
            my_con.commit()
            print("Table created successfully")
        except mysql.connector.Error as err:
            print(f"Error creating table: {err}")


# Function to insert results into MySQL
def insert_results(total_moves, winner, p1_moves, p2_moves, p1_pos, p2_pos, p1_captures, p2_captures, p1_points,
                   p2_points, completed_early):
    if my_con and my_con.is_connected():
        try:
            query = """
                INSERT INTO ludo_mixed_vs_responsible_7_2_36
                (total_moves, winner, player1_moves_used, player2_moves_used, player1_final_positions, player2_final_positions,
                 player1_captures, player2_captures, player1_total_points, player2_total_points, game_completed_early, mixed_bot_probability)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (total_moves, winner, p1_moves, p2_moves, str(p1_pos), str(p2_pos), p1_captures, p2_captures,
                      p1_points, p2_points, completed_early, a)
            cur.execute(query, values)
            my_con.commit()
        except mysql.connector.Error as err:
            print(f"Error inserting data: {err}")


# Main simulation loop
def run_simulations():
    create_table()

    print(f"Running {simul} simulations...")

    for sim in range(1, simul + 1):
        total_moves, winner, p1_captures, p2_captures = play_game()

        # Calculating total points for each player
        p1_points = sum(player_positions['player1'])
        p2_points = sum(player_positions['player2'])

        # Checking if someone got all 4 tokens home
        completed_early = (sum(1 for pos in player_positions['player1'] if pos == HOME_SCORE) == pieces or
                           sum(1 for pos in player_positions['player2'] if pos == HOME_SCORE) == pieces)

        # Inserting results into the ludo database
        insert_results(total_moves, winner, move_count['player1'], move_count['player2'],
                       player_positions['player1'], player_positions['player2'],
                       p1_captures, p2_captures, p1_points, p2_points, completed_early)

        if sim % 1000 == 0:
            print(f"Completed {sim} simulations")

    # Closing the database connection
    if my_con and my_con.is_connected():
        cur.close()
        my_con.close()
        print("MySQL connection closed")


# Running the simulations
run_simulations()
