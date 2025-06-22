import random
import mysql.connector

# Connecting MySQL
try:
    my_con = mysql.connector.connect(host="localhost", user="root", passwd="1234", database="ludo_a_g")
    if my_con.is_connected():
        cur = my_con.cursor()
        print("Connected to MySQL database")
except mysql.connector.Error as err:
    print(f"Error connecting to MySQL: {err}")
    my_con = None

# Number of simulations
simul = 10000

# Datapoints needed for analysis
squares = [13, 11, 9, 7]  # Number of squares per side
pieces = 4  # The number of tokens per player
max_moves_per_player = 18  # Maximum moves per player

# Player tokens

player_positions = {
    'player1': [0 for _ in range(pieces)],
    'player2': [0 for _ in range(pieces)]
}

# Captures
capture_count = {
    'player1': 0,
    'player2': 0
}

# Moves
move_count = {
    'player1': 0,
    'player2': 0
}

# Home Score, safe scores and kill mapping for each board config
for square in squares:
    if square == 13:
        HOME_SCORE = 56
        safe_scores = [0, 8, 13, 21, 26, 34, 39, 47, 51, 52, 53, 54, 55, 56]
        kill_scores = {
            27: 1, 28: 2, 29: 3, 30: 4, 31: 5, 32: 6, 33: 7,
            35: 9, 36: 10, 37: 11, 38: 12, 40: 14, 41: 15,
            42: 16, 43: 17, 44: 18, 45: 19, 46: 20, 48: 22,
            49: 23, 50: 24, 1: 27, 2: 28, 3: 29, 4: 30, 5: 31,
            6: 32, 7: 33, 9: 35, 10: 36, 11: 37, 12: 38, 14: 40,
            15: 41, 16: 42, 17: 43, 18: 44, 19: 45, 20: 46, 22: 48,
            23: 49, 24: 50
        }

    elif square == 11:
        HOME_SCORE = 47
        safe_scores = [0, 22, 43, 44, 45, 46, 47]
        kill_scores = {
            23: 1, 24: 2, 25: 3, 26: 4, 27: 5, 28: 6, 29: 7, 30: 8,
            31: 9, 32: 10, 33: 11, 34: 12, 35: 13, 36: 14, 37: 15, 38: 16,
            39: 17, 40: 18, 41: 19, 42: 20, 1: 23, 2: 24, 3: 25, 4: 26, 5: 27,
            6: 28, 7: 29, 8: 30, 9: 31, 10: 32, 11: 33, 12: 34, 13: 35, 14: 36,
            15: 37, 16: 38, 17: 39, 18: 40, 19: 41, 20: 42
        }

    elif square == 9:
        HOME_SCORE = 38
        safe_scores = [0, 18, 35, 36, 37, 38]
        kill_scores = {
            19: 1, 20: 2, 21: 3, 22: 4, 23: 5, 24: 6,
            25: 7, 26: 8, 27: 9, 28: 10, 29: 11, 30: 12,
            31: 13, 32: 14, 33: 15, 34: 16, 1: 19, 2: 20,
            3: 21, 4: 22, 5: 23, 6: 24, 7: 25, 8: 26, 9: 27,
            10: 28, 11: 29, 12: 30, 13: 31, 14: 32, 15: 33, 16: 34
        }

    elif square == 7:
        HOME_SCORE = 29
        safe_scores = [0, 14, 27, 28, 29]
        kill_scores = {
            15: 1, 16: 2, 17: 3, 18: 4, 19: 5, 20: 6,
            21: 7, 22: 8, 23: 9, 24: 10, 25: 11, 26: 12,
            1: 15, 2: 16, 3: 17, 4: 18, 5: 19, 6: 20, 7: 21,
            8: 22, 9: 23, 10: 24, 11: 25, 12: 26
        }


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
                capture_count[player] += 1  # increasing capture count
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
    best_dice = None
    best_priority = -1 # can be any negative number, jaate first loop e te true deye

    for dice_val in available_dice:
        priority = 0

        # Checking if this dice can promote any token, it is the first priority
        for idx, pos in enumerate(player_positions['player1']):
            if (0 < pos < HOME_SCORE) and (pos + dice_val >= HOME_SCORE):
                priority = max(priority, 4)  # Highest priority, setting priority to 4
                break

        # Checking if this dice can capture opponent token, the second priority
        if priority < 4:
            for idx, pos in enumerate(player_positions['player1']):
                if 0 < pos < HOME_SCORE:
                    new_pos = pos + dice_val
                    mapped_score = kill_scores.get(new_pos)
                    if mapped_score in player_positions['player2']:
                        for opp_idx, opp_pos in enumerate(player_positions['player2']):
                            if opp_pos == mapped_score and not is_safe(mapped_score, 'player2'):
                                priority = max(priority, 3)
                                break
                        if priority == 3:
                            break

        # Checking if this dice moves to safe square, third priority
        if priority < 3:
            for idx, pos in enumerate(player_positions['player1']):
                if 0 < pos < HOME_SCORE:
                    new_pos = pos + dice_val
                    if new_pos in safe_scores:
                        priority = max(priority, 2)
                        break

        # Prefer higher dice values for aggressive play, fourth priority
        if priority < 2:
            priority = 1

        # Select dice with the highest priority and if both the dice has same priority then we go with the dice with higher value
        if (priority > best_priority) or (priority == best_priority and dice_val > best_dice):
            best_dice = dice_val
            best_priority = priority

    return best_dice if best_dice is not None else max(available_dice) #if no best dice choose max


def player2_choose_dice(available_dice):
    best_dice = None
    best_priority = -1

    active_tokens = [i for i, pos in enumerate(player_positions['player2']) if 0 < pos < HOME_SCORE]

    for dice_val in available_dice:
        priority = 0

        # Checking if this dice can promote any token, priority one
        for idx, pos in enumerate(player_positions['player2']):
            if (0 < pos < HOME_SCORE) and (pos + dice_val >= HOME_SCORE):
                priority = max(priority, 6)  # Highest priority, setting priority to 6
                break

        # Checking if this dice can capture opponent token
        if priority < 6:
            for token in [i for i, pos in enumerate(player_positions['player2'])]:
                new_pos = player_positions['player2'][token] + dice_val
                mapped = kill_scores.get(new_pos)
                if mapped in player_positions['player1']:
                    for opp_idx, opp_pos in enumerate(player_positions['player1']):
                        if opp_pos == mapped and not is_safe(mapped, 'player1'):
                            priority = max(priority, 5)
                            break
                    if priority == 5:
                        break

        # Situational aggressive movement when opponent is close to home
        if priority < 5 and any(pos >= 50 for pos in player_positions['player1']):
            if active_tokens:
                priority = max(priority, 4)

        # Checking if this dice moves to safe square
        if priority < 4:
            for token in active_tokens:
                if player_positions['player2'][token] + dice_val in safe_scores:
                    priority = max(priority, 3)
                    break

        # Checking for optimal pair movement
        if priority < 3:
            pair_tokens = [i for i in active_tokens if player_positions['player2'][i] < 26]
            if len(pair_tokens) >= 2:
                priority = max(priority, 2)

            post_26 = [i for i in active_tokens if player_positions['player2'][i] >= 26]
            if len(post_26) >= 2:
                priority = max(priority, 2)

        # Last priority choose max and move the token
        if priority < 2:
            priority = 1

        # Select dice with the highest priority
        if priority > best_priority:
            best_dice = dice_val
            best_priority = priority
        elif priority == best_priority:
            if dice_val > best_dice:
                best_dice = dice_val
    return best_dice if best_dice is not None else max(available_dice)


# Aggressive Bot
def aggressive(dice_val):
    extra_turn = False

    # Promoting a token
    for idx, pos in enumerate(player_positions['player1']):
        if (0 < pos < HOME_SCORE) and (pos + dice_val >= HOME_SCORE):
            new_score, promoted = update_score('player1', idx, dice_val)
            if promoted:
                extra_turn = True
            return extra_turn

    # Capturing an opponent token
    for idx, pos in enumerate(player_positions['player1']):
        if 0 < pos < HOME_SCORE:
            new_pos = pos + dice_val
            mapped_score = kill_scores.get(new_pos)
            if mapped_score in player_positions['player2']:
                opponent_at_pos = False
                for opp_idx, opp_pos in enumerate(player_positions['player2']):
                    if opp_pos == mapped_score and not is_safe(mapped_score, 'player2'):
                        opponent_at_pos = True
                        break

                if opponent_at_pos:
                    new_score, _ = update_score('player1', idx, dice_val)
                    captured = capture_tks(new_score, 'player1')
                    if captured:
                        extra_turn = True
                    return extra_turn

    # Moving to safe square
    for idx, pos in enumerate(player_positions['player1']):
        if 0 < pos < HOME_SCORE:
            new_pos = pos + dice_val
            if new_pos in safe_scores:
                update_score('player1', idx, dice_val)
                return extra_turn

    # Moving first active token
    for idx, pos in enumerate(player_positions['player1']):
        if 0 < pos < HOME_SCORE:
            update_score('player1', idx, dice_val)
            return extra_turn

    # if no tokens are active then activating onne
    for idx, pos in enumerate(player_positions['player1']):
        if pos == 0:
            update_score('player1', idx, dice_val)
            return extra_turn

    return extra_turn


# Responsible-Pair bot
def responsible_pair(dice_val):
    extra_turn = False
    active_tokens = [i for i, pos in enumerate(player_positions['player2']) if 0 < pos < HOME_SCORE]

    # Promoting a token
    for token in active_tokens:
        if player_positions['player2'][token] + dice_val >= HOME_SCORE:
            new_score, promoted = update_score('player2', token, dice_val)
            if promoted:
                extra_turn = True
            return extra_turn

    # Capturing one token
    for token in active_tokens:
        new_pos = player_positions['player2'][token] + dice_val
        mapped = kill_scores.get(new_pos)
        if mapped in player_positions['player1']:
            opponent_at_pos = False
            for opp_idx, opp_pos in enumerate(player_positions['player1']):
                if opp_pos == mapped and not is_safe(mapped, 'player1'):
                    opponent_at_pos = True
                    break

            if opponent_at_pos:
                new_score, _ = update_score('player2', token, dice_val)
                captured = capture_tks(new_score, 'player2')
                if captured:
                    extra_turn = True
                return extra_turn

    # Situational aggressive movement
    if any(pos >= 50 for pos in player_positions['player1']):
        if active_tokens:
            highest_token = max(active_tokens, key=lambda i: player_positions['player2'][i])
            update_score('player2', highest_token, dice_val)
            return extra_turn

    # Moving to Safe Square
    for token in active_tokens:
        if player_positions['player2'][token] + dice_val in safe_scores:
            update_score('player2', token, dice_val)
            return extra_turn

    # Chasing opponent using last 2 tokens
    if len(active_tokens) >= 2:
        last_two = sorted(active_tokens, key=lambda i: player_positions['player2'][i])[-2:]
        for token in last_two:
            for opp_pos in player_positions['player1']:
                if 0 < opp_pos < HOME_SCORE:
                    if abs((player_positions['player2'][token] + dice_val) - opp_pos) <= 6:
                        update_score('player2', token, dice_val)
                        return extra_turn

    # Pair movement before reaching 26, I have started from 0 so instead of 27 I have a safe square at 26
    pair_tokens = [i for i in active_tokens if player_positions['player2'][i] < 26]
    if len(pair_tokens) >= 2:
        first = min(pair_tokens, key=lambda i: player_positions['player2'][i])
        update_score('player2', first, dice_val)
        return extra_turn

    # Paired movement after all reached 26
    post_26 = [i for i in active_tokens if player_positions['player2'][i] >= 26]
    if len(post_26) >= 2:
        first = min(post_26, key=lambda i: player_positions['player2'][i])
        update_score('player2', first, dice_val)
        return extra_turn

    # move first active token or activate new token
    if active_tokens:
        update_score('player2', active_tokens[0], dice_val)
        return extra_turn

    # Trying to activate a token
    for idx, pos in enumerate(player_positions['player2']):
        if pos == 0:
            update_score('player2', idx, dice_val)
            return extra_turn

    return extra_turn


# Check if game is won
def check_winner():
    player1_home = sum(1 for pos in player_positions['player1'] if pos == HOME_SCORE)
    player2_home = sum(1 for pos in player_positions['player2'] if pos == HOME_SCORE)

    if player1_home == pieces:
        return 'player1'
    elif player2_home == pieces:
        return 'player2'
    else:
        return None


# Function to determine winner by points
def determine_winner_by_points():
    player1_total = sum(player_positions['player1'])
    player2_total = sum(player_positions['player2'])

    if player1_total > player2_total:
        return 'player1'
    elif player2_total > player1_total:
        return 'player2'
    else:
        return 'tie'  # In case of exact tie


# Execute a single move for a player
def execute_move(player, dice_value):
    move_count[player] += 1

    if player == 'player1':
        extra_turn = aggressive(dice_value)
    else:
        extra_turn = responsible_pair(dice_value)

    # Check for extra turn due to six or capture
    if dice_value == 6 or extra_turn:
        return True  # Indicates extra turn earned

    return False


# Gameplay function
def play_game():
    global player_positions, capture_count, move_count

    # Reset positions, capture counts, and move counts
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
    current_roller = 'player1'  # since player 1 rolls the dice first then roller will be 2 and so on

    # Continue until someone wins or both players exhaust their moves
    while (move_count['player1'] < max_moves_per_player or
           move_count['player2'] < max_moves_per_player) and not winner:

        # Rolling 3 dice
        dice_vals = dice_roll()
        available_dice = dice_vals.copy()

        # Three moves per dice roll cycle
        moves_in_cycle = []

        # Determine the sequence based on who's rolling
        if current_roller == 'player1':
            moves_in_cycle = ['player1', 'player2', 'player1']
        else:
            moves_in_cycle = ['player2', 'player1', 'player2']

        extra_turn_earned = False

        for move_num, current_player in enumerate(moves_in_cycle):
            if not available_dice:
                break

            # Check if player has moves left
            if move_count[current_player] >= max_moves_per_player:
                continue

            # Player chooses dice
            if current_player == 'player1':
                chosen_dice = player1_choose_dice(available_dice)
            else:
                chosen_dice = player2_choose_dice(available_dice)

            available_dice.remove(chosen_dice)

            # Execute move
            earned_extra = execute_move(current_player, chosen_dice)
            if earned_extra:
                extra_turn_earned = True

            total_moves += 1

            # Check for winner after each move
            winner = check_winner()
            if winner:
                break

        # Handle extra turn logic
        if extra_turn_earned and not winner:
            pass
        else:
            # Switch roller for next round
            current_roller = 'player2' if current_roller == 'player1' else 'player1'

    # If no winner after all moves are exhausted, determine by total points
    if not winner:
        winner = determine_winner_by_points()

    return total_moves, winner, capture_count['player1'], capture_count['player2']


# Function to create MySQL table
def create_table(sq_num, pc, move):
    if my_con and my_con.is_connected():
        try:
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS ludo_{sq_num}_{pc}_{move} (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    squares INT,
                    pieces INT,
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
                    game_completed_early BOOLEAN
                )
            """)
            my_con.commit()
            print(f"Creating and inserting into table: ludo_{sq_num}_{pc}_{move}")
        except mysql.connector.Error as err:
            print(f"Error creating table: {err}")


# Function to insert results into MySQL
def insert_results(sq_num, pc, move, total_moves, winner, p1_moves, p2_moves, p1_pos, p2_pos, p1_captures, p2_captures, p1_points,
                   p2_points, completed_early):
    if my_con and my_con.is_connected():
        try:
            table_name = f"ludo_{sq_num}_{pc}_{move}"
            query = f"""
                INSERT INTO {table_name}
                (squares, pieces, total_moves, winner, player1_moves_used, player2_moves_used, player1_final_positions, player2_final_positions,
                 player1_captures, player2_captures, player1_total_points, player2_total_points, game_completed_early)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (sq_num, pc, total_moves, winner, p1_moves, p2_moves, str(p1_pos), str(p2_pos), p1_captures, p2_captures,
                      p1_points, p2_points, completed_early)
            cur.execute(query, values)
            my_con.commit()
        except mysql.connector.Error as err:
            print(f"Error inserting data: {err}")


# Main simulation loop
def run_simulations(sq_num, pc, move):
    create_table(sq_num, pc, move)

    print(f"Running {simul} simulations...")

    for sim in range(1, simul + 1):
        total_moves, winner, p1_captures, p2_captures = play_game()

        # Calculating total points for each player
        p1_points = sum(player_positions['player1'])
        p2_points = sum(player_positions['player2'])

        # Check if someone got all 4 tokens home
        completed_early = (sum(1 for pos in player_positions['player1'] if pos == HOME_SCORE) == pieces or
                           sum(1 for pos in player_positions['player2'] if pos == HOME_SCORE) == pieces)

        # Insert results into the ludo database
        insert_results(sq_num, pc, move, total_moves, winner, move_count['player1'], move_count['player2'],
                       player_positions['player1'], player_positions['player2'],
                       p1_captures, p2_captures, p1_points, p2_points, completed_early)

        if sim % 1000 == 0:
            print(f"Completed {sim} simulations")




# Run the simulations

for square_num in squares:
    for piece in [4, 3, 2]:
        for moves in [18, 24, 30, 36]:
            run_simulations(square_num, piece, moves)


# Close the database connection
if my_con and my_con.is_connected():
    cur.close()
    my_con.close()
    print("MySQL connection closed")
