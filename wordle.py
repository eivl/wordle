import curses
import random


class Wordle:
    """
    A word guessing game.
    """
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

    def __init__(self):
        """
        Initialize the game.
        """
        self.line = 1
        self.buffer = []
        self.past_guesses = []
        self.current_word = ''
        self._read_wordlist()
        curses.wrapper(self.run)

    def _read_wordlist(self):
        """
        Read the wordlist file into memory. and pick a random word.
        """
        with open('wordlist') as f:
            self.wordlist = f.read().splitlines()
        self.word = random.choice(self.wordlist)

    @staticmethod
    def color_word(word, guess) -> list[tuple[int, int]]:
        """
        Return a list of tuples of the form (color_pair, position) for
        each correct letter in the guess.
        :param word:
        :param guess:
        :return: list of tuples of the form (color_pair, position)
        """
        result = []
        letters = list(word)
        for i, (c1, c2) in enumerate(zip(word, guess)):
            if c1 == c2:
                result.append((Wordle.GREEN_PAIR, i))
                letters.remove(c1)
        for i, (c1, c2) in enumerate(zip(word, guess)):
            if c1 != c2 and c2 in letters:
                result.append((Wordle.YELLOW_PAIR, i))
                letters.remove(c2)
        return result

    def run(self, stdscr: curses.window) -> int:
        """
        Main game loop.
        :param stdscr:
        :return: int
        """
        self.init_pairs()
        while True:
            self.line = 1
            stdscr.clear()
            self.show_guesses(stdscr)

            # end the game if the user has guessed the word or tried 6 times.
            if len(self.past_guesses) == 6 or self.past_guesses and self.past_guesses[-1] == self.word:
                return self.end_game(stdscr)

            self.draw_current_word(stdscr)
            self.guess_word(stdscr)
            char = self.get_character(stdscr)
            self.update_current_word(char)

    def update_current_word(self, char) -> None:
        """
        Update the current word with the given character or remove the
        last character with backspace.
        :param char:
        :return: None
        """
        if char == '\b':
            self.current_word = self.current_word[:-1]
        elif len(self.current_word) < 5 and isinstance(char, str) and char.isalnum() and char.isascii():
            self.current_word += char.lower()

    def get_character(self, stdscr) -> int | str:
        """
        Get a character from the buffer or from the user.
        :param stdscr:
        :return: int or str
        """
        if self.buffer:
            char = self.buffer.pop()
        else:
            char = stdscr.get_wch()
        return char

    def guess_word(self, stdscr) -> None:
        """
        Guess the word if the user has entered 5 characters.
        If the word is in the wordlist, ask the user to confirm the word
        with enter. If the word is not in the wordlist, show an error.
        :param stdscr:
        :return: None
        """
        if len(self.current_word) == 5:
            if self.current_word in self.wordlist:
                stdscr.addstr(
                    self.line,
                    15,
                    'press enter to accept',
                    curses.color_pair(self.CYAN_PAIR),
                )
                char = stdscr.get_wch()
                self.buffer.append(char)
                if char == '\n':
                    self.past_guesses.append(self.current_word)
                    self.current_word = ''
            else:
                stdscr.addstr(
                    self.line,
                    15,
                    'word not in wordlist!',
                    curses.color_pair(self.RED_PAIR),
                )

    def draw_current_word(self, stdscr) -> None:
        """
        Draw the current word. Including underlines for each character.
        :param stdscr:
        :return:
        """
        stdscr.addstr(self.line, 1, ' '.join(self.current_word))
        for i in range(5):
            stdscr.chgat(self.line, 1 + i * 2, 1, curses.A_UNDERLINE)

    def end_game(self, stdscr) -> int:
        """
        End the game and show the user the result.
        White squares indicate letters that are not in the word.
        Green squares indicate letters that are in the correct position.
        Yellow squares indicate letters that are in the word but not in
        the correct position.
        :param stdscr:
        :return: int
        """
        for past_guess in self.past_guesses:
            word_chars = [self.WHITE] * 5
            for pair, pos in self.color_word(self.word, past_guess):
                word_chars[pos] = self.COLOR_PAIR_MAP[pair]
            stdscr.addstr(self.line, 0, ''.join(word_chars))
            self.line += 1
        self.line += 1
        if self.past_guesses[-1] == self.word:
            stdscr.addstr(self.line, 0, 'CONGRATULATION YOU WON!')
        else:
            stdscr.addstr(self.line, 0, f'BETTER LUCK NEXT TIME!')
            self.line += 1
            stdscr.addstr(self.line, 0, f'THE WORD WAS: {self.word}')
        stdscr.addstr(self.line + 1, 0, '(press a key to quit)')
        stdscr.get_wch()
        return 0

    def show_guesses(self, screen) -> None:
        """
        Show the past guesses. Color the letters in the word according
        to the following rules:
        Green: letter is in the correct position
        Yellow: letter is in the word but not in the correct position
        :param screen:
        :return:
        """
        for past_guess in self.past_guesses:
            screen.addstr(self.line, 1, ' '.join(past_guess))
            for pair, pos in self.color_word(self.word, past_guess):
                screen.chgat(self.line, 1 + 2 * pos, 1, curses.color_pair(pair))
            self.line += 2

    @staticmethod
    def init_pairs() -> None:
        """
        Initialize the color pairs.
        :return:
        """
        curses.init_pair(Wordle.GREEN_PAIR, curses.COLOR_BLACK, curses.COLOR_GREEN)
        curses.init_pair(Wordle.YELLOW_PAIR, curses.COLOR_BLACK, curses.COLOR_YELLOW)
        curses.init_pair(Wordle.RED_PAIR, curses.COLOR_BLACK, curses.COLOR_RED)
        curses.init_pair(Wordle.CYAN_PAIR, curses.COLOR_BLACK, curses.COLOR_CYAN)


if __name__ == '__main__':
    raise SystemExit(Wordle())
