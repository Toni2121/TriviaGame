import psycopg2

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
    password VARCHAR(100) NOT NULL,  -- better to encrypt
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
    PRIMARY KEY (player_id, question_id) -- Composite primary key
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS high_scores (
    score_id INTEGER PRIMARY KEY CHECK (score_id >= 1 AND score_id <= 20), -- representing scores from 1 to 20
    player_id INTEGER REFERENCES players(player_id) ON DELETE CASCADE,
    achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
''')

conn.commit()


def statistics():
    """
    Displays different types of statistics by choice.
    """
    cursor.execute("SELECT count(*) FROM players")
    player_count = cursor.fetchone()[0]
    print(f"Amount of players played so far: {player_count}")

    cursor.execute("""
    SELECT q.question_id, q.question_text, COUNT(pa.selected_answer) AS correct_answers_count
    FROM player_answers pa
    JOIN questions q ON pa.question_id = q.question_id
    WHERE pa.is_correct = TRUE
    GROUP BY q.question_id, q.question_text
    ORDER BY correct_answers_count DESC;
    """)
    questions_with_most_correct_answers = cursor.fetchall()
    if questions_with_most_correct_answers:
        print("Questions with the most correct answers:")
        for question in questions_with_most_correct_answers:
            print(f"ID: {question[0]}, Question: {question[1]}, Correct Answers: {question[2]}")
    else:
        print("No questions with correct answers found.")

    cursor.execute("""
    SELECT q.question_id, q.question_text, COUNT(pa.selected_answer) AS correct_answers_count
    FROM player_answers pa
    JOIN questions q ON pa.question_id = q.question_id
    WHERE pa.is_correct = TRUE
    GROUP BY q.question_id, q.question_text
    ORDER BY correct_answers_count;
    """)
    questions_with_least_correct_answers = cursor.fetchall()
    if questions_with_least_correct_answers:
        print("Questions with the least correct answers:")
        for question in questions_with_least_correct_answers:
            print(f"ID: {question[0]}, Question: {question[1]}, Correct Answers: {question[2]}")
    else:
        print("No questions with correct answers found.")

    cursor.execute("""
        SELECT p.username, p.questions_solved AS correct_answers_leadeboard
        FROM players p
        ORDER BY correct_answers_leadeboard DESC
        """)
    correct_answers_leadeboard = cursor.fetchall()
    for answer in correct_answers_leadeboard:
        print(f"Username: {answer[0]}, Number of correct answers: {answer[1]}")

    cursor.execute("""
        SELECT p.username, COUNT(pa.selected_answer) AS questions_answered_count
        FROM players p
        LEFT JOIN player_answers pa ON p.player_id = pa.player_id
        GROUP BY p.username
        ORDER BY questions_answered_count DESC;
    """)
    answered_questions = cursor.fetchall()
    for answered in answered_questions:
        print(f"Username: {answered[0]}, Questions answered: {answered[1]}")

    while True:
        try:

            player_id_input = int(input("Enter the player ID to view statistics: "))

            cursor.execute("""
                SELECT p.username, p.player_id, q.question_text, pa.selected_answer, pa.is_correct
                FROM players p
                LEFT JOIN player_answers pa ON p.player_id = pa.player_id
                LEFT JOIN questions q ON pa.question_id = q.question_id
                WHERE p.player_id = %s
            """, (player_id_input,))

            player_answers_details = cursor.fetchall()

            if player_answers_details:
                for answer in player_answers_details:
                    print(
                        f"Username: {answer[0]}, Player ID: {answer[1]}, Question: {answer[2]}, Answered: {answer[3]}, Correct: {answer[4]}")
                break
            else:
                print(f"No statistics found for Player ID: {player_id_input}")

        except ValueError:
            print("Invalid input! Please enter a valid player ID (integer).")
        except Exception as e:
            print(f"An error occurred: {e}")
            break

