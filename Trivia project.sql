
CREATE TABLE questions (
    question_id SERIAL PRIMARY KEY,
    question_text TEXT NOT NULL,
    answer_a TEXT NOT NULL,
    answer_b TEXT NOT NULL,
    answer_c TEXT NOT NULL,
    answer_d TEXT NOT NULL,
    correct_answer CHAR(1) CHECK (correct_answer IN ('a', 'b', 'c', 'd')) NOT NULL
);

CREATE TABLE players (
    player_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    age INTEGER NOT NULL,
    questions_solved INTEGER DEFAULT 0
);

CREATE TABLE player_answers (
    player_id INTEGER REFERENCES players(player_id) ON DELETE CASCADE,
    question_id INTEGER REFERENCES questions(question_id) ON DELETE CASCADE,
    selected_answer CHAR(1) CHECK (selected_answer IN ('a', 'b', 'c', 'd')) NOT NULL,
    is_correct BOOLEAN NOT NULL,
    PRIMARY KEY (player_id, question_id)
);


CREATE TABLE high_scores (
    score_id INTEGER PRIMARY KEY CHECK (score_id >= 1 AND score_id <= 20),
    player_id INTEGER REFERENCES players(player_id) ON DELETE CASCADE,
    achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


INSERT INTO questions (question_id, question_text, answer_a, answer_b, answer_c, answer_d, correct_answer)
VALUES
(1, 'Which club has won the most UEFA Champions League titles?', 'Barcelona', 'Real Madrid', 'AC Milan', 'Liverpool', 'B'),
(2, 'Who is the only player to win the World Cup as both a player and a coach?', 'Franz Beckenbauer', 'Carlos Bilardo', 'Vicente del Bosque', 'Johan Cruyff', 'A'),
(3, 'Which country has the 2nd most Copa América titles?', 'Argentina', 'Uruguay', 'Brazil', 'Chile', 'B'),
(4, 'Which player scored the fastest hat-trick in Premier League history?', 'Sergio Agüero', 'Sadio Mané', 'Robbie Fowler', 'Cristiano Ronaldo', 'B'),
(5, 'Which club is known as "The Old Lady" of Italian football?', 'AC Milan', 'Juventus', 'Inter Milan', 'Napoli', 'B'),
(6, 'Who is the youngest player to score in a World Cup final?', 'Pelé', 'Kylian Mbappé', 'Geoff Hurst', 'Thomas Müller', 'A'),
(7, 'Which manager has won the most UEFA Champions League titles?', 'Pep Guardiola', 'Carlo Ancelotti', 'Alex Ferguson', 'Zinedine Zidane', 'B'),
(8, 'In which year did the Ballon dOr first get awarded?', '1956', '1962', '1970', '1984', 'A'),
(9, 'Which club holds the record for the longest unbeaten run in Europe’s top five leagues?', 'Arsenal', 'AC Milan', 'Juventus', 'Bayern Munich', 'A'),
(10, 'Who was the first goalkeeper to win the Ballon dOr?', 'Gianluigi Buffon', 'Lev Yashin', 'Dino Zoff', 'Manuel Neuer', 'B'),
(11, 'Which African country was the first to qualify for a FIFA World Cup?', 'Ghana', 'Egypt', 'Morocco', 'Nigeria', 'B'),
(12, 'Who scored the winning goal in the 2010 FIFA World Cup final?', 'Xavi', 'David Villa', 'Fernando Torres', 'Andrés Iniesta', 'D'),
(13, 'Which club has the nickname "Los Colchoneros"?', 'Real Madrid', 'Sevilla', 'Atlético Madrid', 'Valencia', 'C'),
(14, 'Who is the only player to win the Golden Boot in three different FIFA World Cups?', 'Ronaldo Nazário', 'Miroslav Klose', 'Just Fontaine', 'Nobody', 'D'),
(15, 'What is the only country to have appeared in every FIFA World Cup since its inception?', 'Brazil', 'Germany', 'Italy', 'Argentina', 'A'),
(16, 'Which club did Zlatan Ibrahimović win his first league title with?', 'Ajax', 'Juventus', 'AC Milan', 'Inter Milan', 'A'),
(17, 'Which footballer is nicknamed "The Pharaoh"?', 'Mahmoud Hassan (Trezeguet)', 'Mohamed Salah', 'Ahmed Hegazi', 'Amr Zaki', 'B'),
(18, 'Which team won the first ever Premier League title in 1992/93?', 'Arsenal', 'Manchester United', 'Blackburn Rovers', 'Leeds United', 'B'),
(19, 'Which club has the most Bundesliga titles?', 'Borussia Dortmund', 'Hamburg', 'Schalke 04', 'Bayern Munich', 'D'),
(20, 'Who holds the record for most goals scored in a calendar year?', 'Cristiano Ronaldo', 'Pelé', 'Lionel Messi', 'Gerd Müller', 'C');

);