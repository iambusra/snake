import curses # For the terminal interface
import random # For generating random food positions
import os # For file operations

HIGHSCORE_FILE = 'highscores.txt'

def main(stdscr):
    while True:
        # Initialize the screen
        curses.curs_set(0)
        sh, sw = stdscr.getmaxyx()
        w = curses.newwin(sh, sw, 0, 0)
        w.keypad(1)
        w.timeout(150)

        # Display start screen
        start_screen(w)

        # Initial snake position and length
        snake_x = sw // 4
        snake_y = sh // 2
        snake = [
            [snake_y, snake_x],
            [snake_y, snake_x - 1],
            [snake_y, snake_x - 2]
        ]

        # Initial food position
        food = [sh // 2, sw // 2]
        w.addch(int(food[0]), int(food[1]), '@')  

        # Initial key direction
        key = curses.KEY_RIGHT

        # Initialize score
        score = 0
        speed = 150

        while True:
            next_key = w.getch()
            key = key if next_key == -1 else next_key

            # Calculate the new head of the snake
            new_head = [snake[0][0], snake[0][1]]

            if key == curses.KEY_DOWN:
                new_head[0] += 1
            if key == curses.KEY_UP:
                new_head[0] -= 1
            if key == curses.KEY_LEFT:
                new_head[1] -= 1
            if key == curses.KEY_RIGHT:
                new_head[1] += 1

            # Insert new head
            snake.insert(0, new_head)

            # Check if snake hits the wall or itself
            if (
                snake[0][0] in [0, sh]
                or snake[0][1] in [0, sw]
                or snake[0] in snake[1:]
            ):
                curses.endwin()
                if not end_screen(score):
                    return
                break

            # Check if snake has eaten the food
            if snake[0] == food:
                score += 1
                food = None
                while food is None:
                    nf = [
                        random.randint(1, sh - 2),
                        random.randint(1, sw - 2)
                    ]
                    food = nf if nf not in snake else None
                w.addch(food[0], food[1], '@')  
                if speed > 20:
                    speed -= 5
                w.timeout(speed)
            else:
                # Move snake
                tail = snake.pop()
                w.addch(tail[0], tail[1], ' ')

            w.addch(snake[0][0], snake[0][1], curses.ACS_CKBOARD)

            # Display the score
            w.addstr(0, 2, f'Score: {score}')

def start_screen(w):
    sh, sw = w.getmaxyx()
    w.clear()
    ascii_art = """
░██████╗███╗░░██╗░█████╗░██╗░░██╗███████╗
██╔════╝████╗░██║██╔══██╗██║░██╔╝██╔════╝
╚█████╗░██╔██╗██║███████║█████═╝░█████╗░░
░╚═══██╗██║╚████║██╔══██║██╔═██╗░██╔══╝░░
██████╔╝██║░╚███║██║░░██║██║░╚██╗███████╗
╚═════╝░╚═╝░░╚══╝╚═╝░░╚═╝╚═╝░░╚═╝╚══════╝
    """
    lines = ascii_art.split('\n')
    art_width = max(len(line) for line in lines)
    art_start_col = (sw - art_width) // 2
    for i, line in enumerate(lines):
        w.addstr((sh // 2 - 8) + i, art_start_col, line)
    start_text = "Press Space to start"
    w.addstr(sh // 2 + 4, (sw - len(start_text)) // 2, start_text)
    high_scores_title = "Highest Scores:"
    w.addstr(sh // 2 + 6, (sw - len(high_scores_title)) // 2, high_scores_title)
    scores = get_highscores()
    for i, (name, score) in enumerate(scores[:3]):
        score_text = f"{i + 1}. {name} - {score}"
        w.addstr(sh // 2 + 8 + i, (sw - len(score_text)) // 2, score_text)
    w.refresh()
    while True:
        key = w.getch()
        if key == ord(' '):
            break
    w.clear()

def end_screen(score):
    stdscr = curses.initscr()
    curses.curs_set(0)
    sh, sw = stdscr.getmaxyx()
    stdscr.clear()
    stdscr.addstr(sh // 2 - 1, (sw - 9) // 2, "Game Over")
    stdscr.addstr(sh // 2, (sw - len(f"Your Score: {score}")) // 2, f"Your Score: {score}")
    if is_highscore(score):
        high_score_art = """
  _______
 |       |
(|       |)
 |       |
  \\     /
   `---'
   _|_|_
        """
        lines = high_score_art.split('\n')
        art_width = max(len(line) for line in lines)
        art_start_col = (sw - art_width) // 2
        art_start_row = sh // 2 - 12  # Adjust the starting row for the ASCII art
        for i, line in enumerate(lines):
            stdscr.addstr(art_start_row + i, art_start_col, line)
        stdscr.addstr(sh // 2, (sw - 35) // 2, "New Highscore! Enter your name:")
        curses.echo()
        name = stdscr.getstr(sh // 2 + 1, (sw - 20) // 2, 20).decode('utf-8')
        add_highscore(name, score)
        stdscr.addstr(sh // 2 + 3, (sw - 15) // 2, "Congratulations!")

    stdscr.addstr(sh // 2 + 5, (sw - 27) // 2, "Press R to replay or Q to quit") # Comes after highscore check
    stdscr.addstr(sh // 2 + 7, (sw - 13) // 2, "Highest Scores:") # Top 3 highscores
    scores = get_highscores()
    for i, (name, score) in enumerate(scores[:3]):
        score_text = f"{i + 1}. {name} - {score}"
        stdscr.addstr(sh // 2 + 9 + i, (sw - len(score_text)) // 2, score_text)

    stdscr.refresh()
    while True:
        key = stdscr.getch()
        if key in [ord('Q'), ord('q')]:
            curses.endwin()
            return False
        elif key in [ord('R'), ord('r')]:
            curses.endwin()
            return True

# Get the highscores from the file
def get_highscores():
    if not os.path.exists(HIGHSCORE_FILE):
        return []
    with open(HIGHSCORE_FILE, 'r') as f:
        scores = [line.strip().split(',') for line in f.readlines()]
        scores = [(name, int(score)) for name, score in scores]
        scores.sort(key=lambda x: x[1], reverse=True)
    return scores

# Add a new highscore to the file
def add_highscore(name, score):
    scores = get_highscores()
    scores.append((name, score))
    scores.sort(key=lambda x: x[1], reverse=True)
    # Keep only the top 3 scores
    if len(scores) > 3:
        scores = scores[:3]
    with open(HIGHSCORE_FILE, 'w') as f:
        for name, score in scores:
            f.write(f"{name},{score}\n")

# Check if the given score is a highscore
def is_highscore(score):
    scores = get_highscores()
    return len(scores) < 3 or score > scores[-1][1]

curses.wrapper(main)

# ASCII art source: https://www.asciiart.eu/miscellaneous/awards
# ASCII text art source: https://fsymbols.com/text-art/     