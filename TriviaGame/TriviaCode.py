import psycopg2
from TriviaStatistics import statistics

conn = psycopg2.connect("dbname='postgres' user=postgres password=admin")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS questions (
    question_id SERIAL PRIMARY KEY,
    question_text TEXT NOT NULL,
    answer_a TEXT NOT NULL,
    answer_b TEXT NOT NULL,
    answer_c TEXT NOT NULL,
    answer_d TEXT NOT NULL,
    correct_answer CHAR(1) CHECK (correct_answer IN ('a', 'b', 'c', 'd')) NOT NULL
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS players (
    player_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    age INTEGER NOT NULL,
    questions_solved INTEGER DEFAULT 0
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS player_answers (
    player_id INTEGER REFERENCES players(player_id) ON DELETE CASCADE,
    question_id INTEGER REFERENCES questions(question_id) ON DELETE CASCADE,
    selected_answer CHAR(1) CHECK (selected_answer IN ('a', 'b', 'c', 'd')) NOT NULL,
    is_correct BOOLEAN NOT NULL,
    PRIMARY KEY (player_id, question_id)
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS high_scores (
    score_id SERIAL PRIMARY KEY,
    player_id INTEGER REFERENCES players(player_id) ON DELETE CASCADE,
    score INTEGER NOT NULL,
    achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
''')

conn.commit()


def menu():
    """
    Displays the menu of the game.
    """
    while True:
        user_menu_input = input(
            "Menu - please select your option:\n"
            "1 - Create new account\n"
            "2 - Log into an existing account\n"
            "3 - Show statistics\n"
            "4 - Quit\n"
            "-> "
        )

        if user_menu_input == '1':
            account_create()
        elif user_menu_input == '2':
            login()
        elif user_menu_input == '3':
            print("Displaying statistics:")
            statistics()
        elif user_menu_input == '4':
            print("Exiting program.")
            break
        else:
            print("Invalid selection. Please try again.")


def is_unique_user(username, email):
    """
    Checking whether the given details are unique.
    """
    cursor.execute('SELECT * FROM players WHERE username = %s OR email = %s', (username, email))
    result = cursor.fetchone()
    return result is None


def account_create():
    """
    Account creation.
    """
    username = input("Please enter your username: ")
    password = input("Please enter your password: ")
    repass = input("Please repeat your password: ")
    email = input("Please enter your email: ")
    age = input("How old are you? ")

    if is_unique_user(username, email):
        if password == repass:
            cursor.execute('INSERT INTO players (username, password, email, age) VALUES (%s, %s, %s, %s)',
                           (username, password, email, age))
            conn.commit()
            print("Account created successfully!")
        else:
            print("Passwords do not match. Try again.")
    else:
        print("Username or email is already taken. Please try a different one.")


def login():
    """
    Giving the ability for the player to login into his account.
    """
    while True:
        try:
            username_login = input("Please enter your username: ")
            password_login = input("Please enter your password: ")

            cursor.execute("SELECT * FROM players WHERE username = %s AND password = %s",
                           (username_login, password_login))

            player = cursor.fetchone()

            if player:
                print("Login successful!")
                player_id = player[0]

                cursor.execute('SELECT MAX(question_id) FROM player_answers WHERE player_id = %s', (player_id,))
                last_answered_question = cursor.fetchone()[0]

                if last_answered_question is None:
                    user_decision = input("No previous game found. New game started! Press ENTER to start.")
                    start_game(player_id)
                else:
                    user_decision = input("Previous game detected!\n"
                                          "Press 1 to continue from where you left off!\n"
                                          "Press 2 to start a new game!\n"
                                          "-> ")
                    if user_decision == '1':
                        print("Continuing from the next question...")
                        start_game(player_id, last_answered_question + 1)
                    elif user_decision == '2':
                        print("Starting a new game...")
                        start_game(player_id)
                    else:
                        print("Invalid input! Please try again.")
            else:
                print("Username or password are incorrect... Please try again!")
        except Exception as e:
            print(f"An error occurred: {e}")


def start_game(player_id, start_question=1):
    """
    Game starting function.
    """
    cursor.execute(
        "SELECT question_id, question_text, answer_a, answer_b, answer_c, answer_d, correct_answer FROM questions ORDER BY RANDOM()"
    )
    questions = cursor.fetchall()

    if not questions:
        print("No questions found in the database!")
        return

    correct_answers = 0
    incorrect_answers = 0
    question_number = start_question
    for question in questions[start_question - 1:]:
        print(f"Question {question_number}: {question[1]}")
        print(f"A) {question[2]}")
        print(f"B) {question[3]}")
        print(f"C) {question[4]}")
        print(f"D) {question[5]}")
        print("------------------------------------")
        print("S) Show your current score")
        print("Q) Quit to main menu")

        selected_answer = input("Select your answer (S - show score , Q - Main menu): ").lower()

        if selected_answer == 's':
            print(f"Correct Answers: {correct_answers}")
            print(f"Incorrect Answers: {incorrect_answers}")
            continue
        elif selected_answer == 'q':
            print("Returning to the main menu...\n")
            update_questions_solved(player_id, correct_answers)
            menu()
            return

        if selected_answer in ['a', 'b', 'c', 'd']:
            correct_answer = question[6].lower()
            is_correct = selected_answer == correct_answer
            if is_correct:
                correct_answers += 1
                print("Correct!\n")
            else:
                incorrect_answers += 1
                print(f"Incorrect. The correct answer was: {correct_answer.upper()}\n")
            store_answer(player_id, question[0], selected_answer, is_correct)
        else:
            print("Invalid answer! Please choose from a, b, c, d, S to show score, or Q to quit.")
        question_number += 1

    update_questions_solved(player_id, correct_answers)
    high_scores_insertion(player_id, correct_answers)


def update_questions_solved(player_id, correct_answers):
    """
    Updates the questions_solved column in the players table.
    """
    cursor.execute('''UPDATE players SET questions_solved = questions_solved + %s WHERE player_id = %s''',
                   (correct_answers, player_id))
    conn.commit()
    print(f"Player {player_id} solved {correct_answers} new question(s)!")


def store_answer(player_id, question_id, selected_answer, is_correct):
    """
    Storing the answers made by the player at the player_answers table.
    """
    cursor.execute('''SELECT * FROM player_answers WHERE player_id = %s AND question_id = %s''',
                   (player_id, question_id))
    existing_answer = cursor.fetchone()

    if existing_answer:
        cursor.execute('''UPDATE player_answers SET selected_answer = %s, is_correct = %s
                          WHERE player_id = %s AND question_id = %s''',
                       (selected_answer, is_correct, player_id, question_id))
        print(f"Updated answer for player {player_id} on question {question_id}.")
    else:
        cursor.execute('''INSERT INTO player_answers (player_id, question_id, selected_answer, is_correct)
                          VALUES (%s, %s, %s, %s)''',
                       (player_id, question_id, selected_answer, is_correct))
        print(f"Stored answer for player {player_id} on question {question_id}.")

    conn.commit()


def high_scores_insertion(player_id, score_id):
    """
    Insert or update the score for the player in the high_scores table.
    The table will store the top 20 unique scores, showing the score,
    the player who achieved it last, and the timestamp when it was achieved.
    The highest score should be displayed first, and the table is limited to 20 rows.
    """
    if score_id <= 0:
        print("Invalid score_id, no insertion.")
        return
    cursor.execute('''
        SELECT score_id FROM high_scores WHERE score_id = %s;
    ''', (score_id,))
    existing_score = cursor.fetchone()
    if existing_score:
        cursor.execute('''
            UPDATE high_scores
            SET player_id = %s, achieved_at = CURRENT_TIMESTAMP
            WHERE score_id = %s;
        ''', (player_id, score_id))
    else:
        cursor.execute('''
            INSERT INTO high_scores (player_id, score_id, achieved_at)
            VALUES (%s, %s, CURRENT_TIMESTAMP);
        ''', (player_id, score_id))
    conn.commit()
    cursor.execute('''
        SELECT score_id, player_id, achieved_at
        FROM high_scores
        ORDER BY score_id DESC, achieved_at DESC
        LIMIT 20;
    ''')
    top_scores = cursor.fetchall()
    top_score_ids = [score[0] for score in top_scores]
    cursor.execute('''
        DELETE FROM high_scores
        WHERE score_id NOT IN %s;
    ''', (tuple(top_score_ids),))
    conn.commit()

    print("Score inserted or updated. Top 20 scores are now updated.")






if __name__ == "__main__":
    menu()


cursor.close()
conn.close()
