import curses
import random

GREEN_PAIR = 1
YELLOW_PAIR = 2
RED_PAIR = 3
CYAN_PAIR = 4
GREEN = '🟩'
YELLOW = '🟨'
WHITE = '🔲'
COLOR_PAIR_MAP = {
    GREEN_PAIR: GREEN,
    YELLOW_PAIR: YELLOW,
}


def color_word(word, guess):
    result = []

    letters = list(word)
    for index, (c1, c2) in enumerate(zip(word, guess)):
        if c1 == c2:
            result.append((GREEN_PAIR, index))
            letters.remove(c1)
    for index, (c1, c2) in enumerate(zip(word, guess)):
        if c1 != c2 and c2 in letters:
            result.append((YELLOW_PAIR, index))
            letters.remove(c2)
    return result


def c_main(stdscr):
    with open('wordlist') as f:
        wordlist = f.read().splitlines()
    word = random.choice(wordlist)

    past_guesses = []
    current_word = ''
    buffer = []

    curses.init_pair(GREEN_PAIR, curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(YELLOW_PAIR, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    curses.init_pair(RED_PAIR, curses.COLOR_BLACK, curses.COLOR_RED)
    curses.init_pair(CYAN_PAIR, curses.COLOR_BLACK, curses.COLOR_CYAN)

    while True:
        stdscr.clear()
        line = 1
        for past_guess in past_guesses:
            stdscr.addstr(line, 1, ' '.join(past_guess))
            for pair, pos in color_word(word, past_guess):
                stdscr.chgat(line, 1 + 2*pos, 1, curses.color_pair(pair))
            line += 2

        if len(past_guesses) == 6 or past_guesses and past_guesses[-1] == word:
            for past_guess in past_guesses:
                word_chars = [WHITE] * 5
                for pair, pos in color_word(word, past_guess):
                   word_chars[pos] = COLOR_PAIR_MAP[pair]
                stdscr.addstr(line, 0, ''.join(word_chars))
                line += 1
            line += 1

            if past_guesses[-1] == word:
                stdscr.addstr(line, 0, 'CONGRATULATION YOU WON!')
            else:
                stdscr.addstr(line, 0, f'BETTER LUCK NEXT TIME!')
                line += 1
                stdscr.addstr(line, 0, f'THE WORD WAS: {word}')
            stdscr.addstr(line+1, 0, '(press a key to quit)')
            stdscr.get_wch()
            return 0

        stdscr.addstr(line, 1, ' '.join(current_word))

        for i in range(5):
            stdscr.chgat(line, 1 + i * 2, 1, curses.A_UNDERLINE)

        if len(current_word) == 5:
            if current_word in wordlist:
                stdscr.addstr(
                    line,
                    15,
                    'press enter to accept',
                    curses.color_pair(CYAN_PAIR),
                )
                ch = stdscr.get_wch()
                if ch == '\n':
                    past_guesses.append(current_word)
                    current_word = ''
                    continue
                else:
                    buffer.append(ch)
            else:
                stdscr.addstr(
                    line,
                    15,
                    'word not in wordlist!',
                    curses.color_pair(RED_PAIR),
                )

        if buffer:
            ch = buffer.pop()
        else:
            ch = stdscr.get_wch()
        if ch == '\b':
            current_word = current_word[:-1]
        elif len(current_word) < 5 and isinstance(ch, str) and ch.isalnum() and ch.isascii():
            current_word += ch.lower()

    return 0


def main():
    return curses.wrapper(c_main)


if __name__ == '__main__':
    raise SystemExit(main())
