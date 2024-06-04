import curses
import random
import os

HIGHSCORE_FILE = 'highscores.txt'

def main(stdscr, show_start_screen=True):
    if show_start_screen:
        start_screen(stdscr)  # Show start screen only if flag is True
    paused = False
    ignore_next_key = False

    # Initialize the screen
    curses.curs_set(0)
    sh, sw = stdscr.getmaxyx()
    w = curses.newwin(sh, sw, 0, 0)
    w.keypad(1)
    w.timeout(150)

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
    w.addch(food[0], food[1], '@')

    # Initial key direction
    key = curses.KEY_RIGHT

    # Initialize score
    score = 0
    speed = 150

    while True:
        next_key = w.getch()

        if paused:
            if next_key == ord(' '):
                paused = False
                w.clear()  # Clear the screen when unpausing
                display_game_state(w, snake, food, score)  # Redraw the game state
                ignore_next_key = True
                w.timeout(speed)  # Restore the game speed
            continue

        if ignore_next_key:
            ignore_next_key = False
            continue  # Skip the rest of the loop in the first iteration after unpausing

        if next_key == ord(' '):
            paused = True
            pause_screen(w)
            w.timeout(-1)  # Infinite wait, game is paused
        elif next_key in [curses.KEY_LEFT, curses.KEY_RIGHT, curses.KEY_UP, curses.KEY_DOWN]:
            if (next_key == curses.KEY_LEFT and key != curses.KEY_RIGHT) or \
               (next_key == curses.KEY_RIGHT and key != curses.KEY_LEFT) or \
               (next_key == curses.KEY_UP and key != curses.KEY_DOWN) or \
               (next_key == curses.KEY_DOWN and key != curses.KEY_UP):
                key = next_key
        elif next_key in [ord('q'), ord('Q')]:
            return  # Exit the function to potentially quit
        elif next_key in [ord('r'), ord('R')]:
            return True  # Return True to indicate a restart request

        # Calculate the new head of the snake
        new_head = [snake[0][0], snake[0][1]]
        if key == curses.KEY_DOWN:
            new_head[0] = (new_head[0] + 1) % sh
        if key == curses.KEY_UP:
            new_head[0] = (new_head[0] - 1) % sh
        if key == curses.KEY_LEFT:
            new_head[1] = (new_head[1] - 1) % sw
        if key == curses.KEY_RIGHT:
            new_head[1] = (new_head[1] + 1) % sw

        # Check for collision with self
        if new_head in snake:
            if not end_screen(score, stdscr):
                return False  # Do not restart
            break

        # Insert new head
        snake.insert(0, new_head)

        # Check if snake has eaten the food
        if snake[0] == food:
            score += 1
            while food in snake or food is None:
                food = [random.randint(1, sh - 2), random.randint(1, sw - 2)]
            w.addch(food[0], food[1], '@')
            if speed > 20:
                speed -= 5
            w.timeout(speed)
        else:
            # Move snake
            tail = snake.pop()
            w.addch(tail[0], tail[1], ' ')

        w.addch(snake[0][0], snake[0][1], curses.ACS_CKBOARD)
        w.addstr(0, 2, f'Score: {score}')

    return True  # Return True to indicate a restart request

def pause_screen(w):
    sh, sw = w.getmaxyx()
    pause_text = "Game Paused - Press Space to Resume"
    w.addstr(sh // 2, (sw - len(pause_text)) // 2, pause_text)
    w.refresh()

def display_game_state(w, snake, food, score):
    w.clear()  # Clear previous texts and drawings
    for segment in snake:
        w.addch(segment[0], segment[1], curses.ACS_CKBOARD)
    w.addch(food[0], food[1], '@')
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

def end_screen(score, stdscr):
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
    stdscr.addstr(sh // 2 + 7, (sw - 13) // 2, "Highest Scores:") # Top 3 highscores
    scores = get_highscores()
    for i, (name, score) in enumerate(scores[:3]):
        score_text = f"{i + 1}. {name} - {score}"
        stdscr.addstr(sh // 2 + 9 + i, (sw - len(score_text)) // 2, score_text)

    stdscr.refresh()
    while True:
        key = stdscr.getch()
        if key in [ord('Q'), ord('q')]:
            return False  # Do not restart
        elif key in [ord('R'), ord('r')]:
            return True  # Restart the game

def get_highscores():
    if not os.path.exists(HIGHSCORE_FILE):
        return []
    with open(HIGHSCORE_FILE, 'r') as f:
        scores = [line.strip().split(',') for line in f.readlines()]
        scores = [(name, int(score)) for name, score in scores]
        scores.sort(key=lambda x: x[1], reverse=True)
    return scores

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

def is_highscore(score):
    scores = get_highscores()
    return len(scores) < 3 or score > scores[-1][1]

def game_loop(stdscr):
    show_start_screen = True
    while True:
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(True)
        result = main(stdscr, show_start_screen)
        if not result:
            break  # Exit the loop if not restarting
        show_start_screen = False  # Do not show the start screen when restarting

curses.wrapper(game_loop)
