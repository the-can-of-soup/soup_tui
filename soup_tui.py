"""
A small module written by Soup for basic text UI and user input.
"""

# TO-DO LIST
# - add functions that use msvcrt.getch() and msvcrt.getche() (msvcrt is a built-in module but only for Windows)
# - input types for list of numbers, list of text, and multiline text
# - maybe input type for file path
# - maybe input type for datetime
# - class for printing text formatted as a table
# - function to format times (e.g. 124.7 becomes '00:02:04.70')

# IMPORTS

from typing import Callable
import platform
import random
import shutil
import math
import time
import os

# GLOBALS & CONSTANTS

_BLOCK_CHARACTERS: list[str] = [' ', '░', '▒', '▓', '█']
if platform.python_implementation() == 'PyPy': # normal block characters break in PyPy for some reason
    _BLOCK_CHARACTERS = [' ', '.', '-', '=', '#']
_PROGRESS_BAR_LENGTH: int = 50

_printed_text: str = ''
_title: str = 'Untitled'
_debug_mode: bool = False
_use_fast_clear: bool = True
_print: Callable = print
_input: Callable = input

# DEFINITIONS

class ANSI:
    """
    Class of ANSI escape codes and escape code generators.
    """
    # Actions
    CLEAR_SCREEN: str = '\033[2J\033[1;1H'
    CLEAR_LINE: str = '\033[2K\033[1G'
    CLEAR_TEXT_AFTER_CURSOR: str = '\033[0K'

    # Formatting
    RESET: str = '\033[0m'
    BOLD: str = '\033[1m'
    UNDERLINE: str = '\033[4m'
    INVERT: str = '\033[7m'

    # Foreground Color
    BLACK: str = '\033[38;5;0m'   ; GRAY: str = '\033[38;5;8m'
    RED: str = '\033[38;5;1m'     ; BRIGHT_RED: str = '\033[38;5;9m'
    GREEN: str = '\033[38;5;2m'   ; BRIGHT_GREEN: str = '\033[38;5;10m'
    YELLOW: str = '\033[38;5;3m'  ; BRIGHT_YELLOW: str = '\033[38;5;11m'
    BLUE: str = '\033[38;5;4m'    ; BRIGHT_BLUE: str = '\033[38;5;12m'
    MAGENTA: str = '\033[38;5;5m' ; BRIGHT_MAGENTA: str = '\033[38;5;13m'
    CYAN: str = '\033[38;5;6m'    ; BRIGHT_CYAN: str = '\033[38;5;14m'
    WHITE: str = '\033[38;5;7m'   ; BRIGHT_WHITE: str = '\033[38;5;15m'

    # Background Color
    BLACK_BG: str = '\033[48;5;0m'   ; GRAY_BG: str = '\033[48;5;8m'
    RED_BG: str = '\033[48;5;1m'     ; BRIGHT_RED_BG: str = '\033[48;5;9m'
    GREEN_BG: str = '\033[48;5;2m'   ; BRIGHT_GREEN_BG: str = '\033[48;5;10m'
    YELLOW_BG: str = '\033[48;5;3m'  ; BRIGHT_YELLOW_BG: str = '\033[48;5;11m'
    BLUE_BG: str = '\033[48;5;4m'    ; BRIGHT_BLUE_BG: str = '\033[48;5;12m'
    MAGENTA_BG: str = '\033[48;5;5m' ; BRIGHT_MAGENTA_BG: str = '\033[48;5;13m'
    CYAN_BG: str = '\033[48;5;6m'    ; BRIGHT_CYAN_BG: str = '\033[48;5;14m'
    WHITE_BG: str = '\033[48;5;7m'   ; BRIGHT_WHITE_BG: str = '\033[48;5;15m'

    @staticmethod
    def place_cursor(row: int = 1, column: int = 1) -> str:
        """
        Returns the ANSI escape code that places the cursor at the specified coordinates.

        :param row: The row to move the cursor to; 1 is the top row.
        :type row: int
        :param column: The column to move the cursor to; 1 is the leftmost column.
        :type column: int
        :return: The ANSI escape code.
        :rtype: str
        """
        return f'\033[{row};{column}H'

    @staticmethod
    def move_cursor_to_column(column: int = 1) -> str:
        """
        Returns the ANSI escape code that moves the cursor to the specified column.

        :param column: The column to move the cursor to; 1 is the leftmost column.
        :type column: int
        :return: The ANSI escape code.
        :rtype: str
        """
        return f'\033[{column}G'

    @staticmethod
    def move_cursor(down: int = 0, forward: int = 0) -> str:
        """
        Returns the ANSI escape code that moves the cursor relative to its current position.

        :param down: The number of spaces down to move the cursor.
        :type down: int
        :param forward: The number of spaces forward to move the cursor.
        :type forward: int
        :return: The ANSI escape code.
        :rtype: str
        """
        x_part: str = ''
        if forward > 0:
            x_part = f'\033[{abs(forward)}C'
        elif forward < 0:
            x_part = f'\033[{abs(forward)}D'

        y_part: str = ''
        if down > 0:
            y_part = f'\033[{abs(down)}B'
        elif down < 0:
            y_part = f'\033[{abs(down)}A'

        return y_part + x_part

    @staticmethod
    def move_cursor_vertical(down: int = 1) -> str:
        """
        Returns the ANSI escape code that moves the cursor down a certain number of lines.

        :param down: The number of lines to move down.
        :type down: int
        :return: The ANSI escape code.
        :rtype: str
        """
        if down > 0:
            return f'\033[{abs(down)}E'
        if down < 0:
            return f'\033[{abs(down)}F'
        return ''

    @staticmethod
    def color(*args: int) -> str:
        """
        Returns the ANSI escape code that changes the text color to a certain ID or RGB value.
        Color IDs defined here: https://en.wikipedia.org/wiki/ANSI_escape_code#8-bit

        :param args: Either a color ID in the range 0-255, or a red, green, and blue component in the range 0-255.
        :type args: int
        :return: The ANSI escape code.
        :rtype: str
        """
        if len(args) not in (1, 3):
            raise ValueError(f'1 or 3 arguments expected, not {len(args)}!')

        if len(args) == 1:
            return f'\033[38;5;{args[0]}m'
        return f'\033[38;2;{args[0]};{args[1]};{args[2]}m'

    @staticmethod
    def background_color(*args: int) -> str:
        """
        Returns the ANSI escape code that changes the text background color to a certain ID or RGB value.
        Color IDs defined here: https://en.wikipedia.org/wiki/ANSI_escape_code#8-bit

        :param args: Either a color ID in the range 0-255, or a red, green, and blue component in the range 0-255.
        :type args: int
        :return: The ANSI escape code.
        :rtype: str
        """
        if len(args) not in (1, 3):
            raise ValueError(f'1 or 3 arguments expected, not {len(args)}!')

        if len(args) == 1:
            return f'\033[48;5;{args[0]}m'
        return f'\033[48;2;{args[0]};{args[1]};{args[2]}m'

    # Aliases

    set_pos: Callable = place_cursor
    set_column: Callable = move_cursor_to_column
    move: Callable = move_cursor
    move_vertical: Callable = move_cursor_vertical
    bg_color: Callable = background_color

    ED: str = CLEAR_SCREEN
    EL: str = CLEAR_LINE
    CUP: Callable = place_cursor
    CHA: Callable = move_cursor_to_column

def format_number(n: int | float | complex, leading_zeroes: int = 1, decimal_places: int | None = None, separate_thousands: bool = True, percentage: bool = False, leave_slot_for_neg_sign: bool = False) -> str:
    """
    Formats a number into a string.

    :param n: The number to be formatted. Supports complex numbers.
    :type n: int | float | complex
    :param leading_zeroes: The minimum width of the integer part of the number (not counting commas).
    :type leading_zeroes: int
    :param decimal_places: The number of decimal places to show, or None to keep the same as the original number.
    :type decimal_places: int | None
    :param separate_thousands: Whether to separate thousands with commas.
    :type separate_thousands: bool
    :param percentage: Whether the number should be formatted as a percentage.
    :type percentage: bool
    :param leave_slot_for_neg_sign: Whether to put a space in the spot of the negative sign for positive numbers to always keep it the same length.
    :type leave_slot_for_neg_sign: bool
    :return: The formatted number as a string.
    :rtype: str
    """

    # handle complex numbers
    if isinstance(n, complex):
        formatted_real: str = format_number(n.real, leading_zeroes, decimal_places, separate_thousands, percentage, leave_slot_for_neg_sign)
        formatted_imag: str = format_number(n.imag, leading_zeroes, decimal_places, separate_thousands, percentage, True) + 'i'

        # if the imaginary component is positive, add a positive sign
        if formatted_imag[0] == ' ': # the imaginary part always has "leave_slot_for_neg_sign" enabled so positive numbers will start with a space
            formatted_imag = '+' + formatted_imag[1:]

        return formatted_real + formatted_imag

    # handle percentages
    if percentage:
        n *= 100

    # round
    if decimal_places is not None:
        n = round(n, decimal_places)

    # format integer part
    integer_part_number: int = math.floor(abs(n))
    integer_part: str = str(integer_part_number)
    if integer_part_number == 0:
        integer_part = ''
    if separate_thousands:
        integer_part = f'{integer_part_number:,}'
    integer_part = integer_part.rjust(leading_zeroes + integer_part.count(','), '0')

    # format decimal part
    decimal_part_number: int = 0
    decimal_part: str = ''
    if decimal_places is None:
        if isinstance(n, int):
            decimal_places = 0
        else:
            decimal_places = len(str(n).split('.')[1])
    if decimal_places > 0:
        decimal_part_number = math.floor((abs(n) % 1) * (10 ** decimal_places))
        decimal_part = f'.{decimal_part_number:0>{decimal_places}}'

    # combine formatted parts
    formatted_number: str = integer_part + decimal_part
    if n < 0 and (integer_part_number != 0 or decimal_part_number != 0): # if both integer part and decimal part are 0, don't show negative sign
        formatted_number = '-' + formatted_number
    elif leave_slot_for_neg_sign:
        formatted_number = ' ' + formatted_number # add a space where the negative sign would go if "leave_slot_for_neg_sign" is enabled
    if percentage:
        formatted_number += '%'
    return formatted_number

def use_fast_clear(enable: bool = True) -> None:
    """
    Enables or disables fast clear for clearing the screen.

    With fast clear on, ANSI escape codes are used to quickly clear the screen.
    With fast clear off, the appropriate system command is used to clear the screen.

    :param enable: Whether to enable fast clear.
    :type enable: bool
    :rtype: None
    """
    global _use_fast_clear

    _use_fast_clear = enable

def is_fast_clear_enabled() -> bool:
    """
    Checks whether fast clear is enabled.

    :return: True if fast clear is enabled.
    :rtype: bool
    """
    return _debug_mode

def clear_screen() -> None:
    """
    Clears all text in the terminal by running the appropriate system command.

    :rtype: None
    """
    global _printed_text

    if _use_fast_clear:
        print_raw(ANSI.CLEAR_SCREEN)
    else:
        if platform.system() == 'Windows':
            os.system('cls')
        else:
            os.system('clear')

    _printed_text = ''

def print_raw(text: str = '') -> None:
    """
    Wrapped version of the print builtin. Does not end with a newline by default.

    :param text: The text to be printed.
    :type text: str
    :rtype: None
    """
    global _printed_text

    _print(text, end='')
    _printed_text += text
    _printed_text = _printed_text.split(ANSI.CLEAR_SCREEN)[-1]

def input_raw(prompt: str = '') -> str:
    """
    Wrapped version of the input builtin.

    :param prompt: The prompt to be shown to the user.
    :type prompt: str
    :return: The user's input.
    :rtype: str
    """
    global _printed_text

    user_input: str = _input(prompt)
    _printed_text += prompt + user_input + '\n'
    _printed_text = _printed_text.split(ANSI.CLEAR_SCREEN)[-1]

    return user_input

# noinspection PyShadowingBuiltins
def print(text: str = '', end: str = '\n', format: str = '', remove_old_formatting: bool = True) -> None:
    """
    Wrapped version of the print builtin. Also removes old text formatting on each print by default.

    :param text: The text to be printed.
    :type text: str
    :param end: Is appended to the end of the main text.
    :type end: str
    :param format: ANSI formatting escape codes to be applied to the text.
    :type format: str
    :param remove_old_formatting: If enabled, old text formatting will be cleared before printing.
    :type remove_old_formatting: bool
    :rtype: None
    """
    if remove_old_formatting:
        format = ANSI.RESET + format

    print_raw(format + text + end)

# noinspection PyShadowingBuiltins
def input(prompt: str = ' > ', prompt_format: str = '', input_format: str = ANSI.CYAN, remove_old_formatting: bool = True) -> str:
    """
    Wrapped version of the input builtin.

    :param prompt: The prompt to be shown to the user.
    :type prompt: str
    :param prompt_format: ANSI formatting escape codes to be applied to the prompt.
    :type prompt_format: str
    :param input_format: ANSI formatting escape codes to be applied to the user's input.
    :type input_format: str
    :param remove_old_formatting: If enabled, old text formatting will be cleared before printing.
    :type remove_old_formatting: bool
    :return: The user's input.
    :rtype: str
    """
    global  _printed_text

    if remove_old_formatting:
        prompt_format = ANSI.RESET + prompt_format

    user_input: str = _input(prompt_format + prompt + input_format)
    _printed_text += prompt_format + prompt + input_format + user_input + '\n'
    _printed_text = _printed_text.split(ANSI.CLEAR_SCREEN)[-1]

    return user_input

# noinspection PyShadowingBuiltins
def print_debug(text: str = '', end: str = '\n', format: str = ANSI.GRAY) -> None:
    """
    Prints text only if debug mode is on.

    :param text: The text to be printed.
    :type text: str
    :param end: Is appended to the end of the main text.
    :type end: str
    :param format: ANSI formatting escape codes to be applied to the text.
    :type format: str
    :rtype: None
    """
    if _debug_mode:
        print('[DEBUG] ' + text, end, format)

def debug_mode(enable_debug_mode: bool = True) -> None:
    """
    Enables or disables debug mode for ``print_debug()``.

    :param enable_debug_mode: Whether to enable debug mode.
    :type enable_debug_mode: bool
    :rtype: None
    """
    global _debug_mode

    _debug_mode = enable_debug_mode

def is_debug_mode() -> bool:
    """
    Checks whether debug mode is enabled.

    :return: True if debug mode is enabled.
    :rtype: bool
    """
    return _debug_mode

def reprint(text: str | None = None) -> None:
    """
    Clears all text in the terminal, and then prints the same text again.
    Optionally providing a string will print that instead.

    :param text: The text to be printed after the screen clear, or None to print the old text again.
    :type text: str | None
    :rtype: None
    """
    if text is None:
        text = _printed_text

    clear_screen()
    print_raw(text)

def get_displayed_text() -> str:
    """
    Returns all text currently displayed in the terminal.

    :return: The text displayed in the terminal.
    :rtype: str
    """
    return _printed_text

def get_title() -> str:
    """
    Returns the current default title set by ``set_title()``.

    :return: The default title.
    :rtype: str
    """
    return _title

def set_title(text: str) -> None:
    """
    Sets the default title for ``print_title()``.

    :param text: The text to become the default title.
    :type text: str
    :rtype: None
    """
    global _title

    _title = text

def print_title(text: str | None = None, clear_screen_first: bool = True) -> None:
    """
    Prints text in a title format.

    :param text: The title to be printed, or None to print the title set by ``set_title()``.
    :type text: str | None
    :param clear_screen_first: Whether to clear the screen first.
    :type clear_screen_first: bool
    :rtype: None
    """
    if text is None:
        text = _title

    if clear_screen_first:
        clear_screen()

    print(text.upper())
    print('-' * max(len(text) + 2, 20))
    print()

def show_progress_bar(text: str, progress: float, finished: bool = False, start_time: float | None = None) -> None:
    """
    Displays a progress bar.

    :param text: Text to be displayed at the front of the progress bar.
    :type text: str
    :param progress: The progress level of the progress bar from 0 to 1.
    :type progress: float
    :param finished: If True, the progress bar will be printed normally; if False, it will have a carriage return at the end.
    :type finished: bool
    :param start_time: The unix timestamp that the process started, or None to disable ETA display.
    :type start_time: float | None
    :rtype: None
    """
    num_block_characters: int = len(_BLOCK_CHARACTERS)

    # generate main progress bar
    progress_bar: str = ''
    for i in range(_PROGRESS_BAR_LENGTH):
        block_progress: float = progress * _PROGRESS_BAR_LENGTH - i
        if block_progress > 1:
            block_progress = 1
        elif block_progress < 0:
            block_progress = 0

        block_character: str = _BLOCK_CHARACTERS[math.floor(block_progress * (num_block_characters - 1))]
        progress_bar += block_character

    # generate ETA
    eta: str = ''
    if start_time is not None and 0 < progress < 1:
        now: float = time.time()
        delta_time: float = now - start_time
        if delta_time > 10: # only show ETA after 10 seconds have passed to give a more accurate prediction
            estimated_remaining: float = (delta_time / progress) * (1 - progress)
            eta = f' (ETA {str(math.floor(estimated_remaining / 3600)).zfill(2)}:{str(math.floor(estimated_remaining / 60) % 60).zfill(2)}:{str(math.floor(estimated_remaining) % 60).zfill(2)})'

    # print to terminal
    end: str = '\r'
    if finished:
        end = '\n'
    print(f'{text} [{ANSI.GREEN}{progress_bar}{ANSI.RESET}] {ANSI.GREEN}{math.floor(progress * 100000) / 1000:.3f}%{eta}' + ANSI.CLEAR_TEXT_AFTER_CURSOR, end=end)

class ProgressBar:
    """
    A progress bar to be displayed in the terminal.
    """
    def __init__(self, text: str = 'Loading...', progress: float = 0, max_progress: float = 1, start_time: float | None = None) -> None:
        """
        Initializes the progress bar.

        :param text: Text to be displayed at the front of the progress bar.
        :type text: str
        :param progress: The progress level of the progress bar.
        :type progress: float
        :param max_progress: The maximum value for ``progress`` (i.e. the progress bar is at 100% when ``progress`` is this value.)
        :type max_progress: float
        :param start_time: The unix timestamp that the process started, or None to use the current timestamp.
        :type start_time: float | None
        :rtype: None
        """
        self.text: str = text
        self.progress: float = progress
        self.max_progress: float = max_progress
        self.start_time: float = time.time() if start_time is None else start_time

    def set_text(self, text: str) -> None:
        """
        Changes the text to be displayed at the front of the progress bar.

        :param text: The new text for the progress bar.
        :type text: str
        :rtype: None
        """
        self.text = text

    def set_progress(self, progress: float):
        """
        Changes the progress level.

        :param progress: The new progress level.
        :type progress: float
        :rtype: None
        """
        self.progress = progress

    def show(self, progress: float | None = None) -> None:
        """
        Optionally changes the progress level and prints the progress bar.

        :param progress: The new progress level of the progress bar, or None to leave unchanged.
        :type progress: float | None
        :rtype: None
        """
        if progress is not None:
            self.progress = progress

        show_progress_bar(self.text, self.progress / self.max_progress, False, self.start_time)

    def finish(self) -> None:
        """
        Prints the final state of the progress bar.

        :rtype: None
        """
        show_progress_bar(self.text, 1, True, self.start_time)

def wait_for_enter(action: str = 'continue') -> None:
    """
    Waits for the user to press ENTER by showing the text "Press ENTER to {action}."

    :param action: Should be a single word or phrase describing what pressing ENTER will do.
    :type action: str
    :rtype: None
    """
    input(f'Press ENTER to {action}.')

def press_enter_to_start() -> None:
    """
    Same as ``wait_for_enter('start')``.

    :rtype: None
    """
    wait_for_enter('start')

def press_enter_to_play() -> None:
    """
    Same as ``wait_for_enter('play')``.

    :rtype: None
    """
    wait_for_enter('play')

def press_enter_to_finish() -> None:
    """
    Same as ``wait_for_enter('finish')``.

    :rtype: None
    """
    wait_for_enter('finish')

def press_enter_to_close() -> None:
    """
    Same as ``wait_for_enter('close')``.

    :rtype: None
    """
    wait_for_enter('close')

def press_enter_to_retry() -> None:
    """
    Same as ``wait_for_enter('retry')``.

    :rtype: None
    """
    wait_for_enter('retry')

def text_input(prompt: str | None = None, end: str = '\n', min_length: int | None = None, max_length: int | None = None, character_whitelist: list[str] | None = None, character_blacklist: list[str] | None = None, fallback_if_blank: str | None = None, keep_asking_until_valid: bool = False) -> str | None:
    """
    Prompts the user for a text input.

    :param prompt: The title of the input to be displayed to the user.
    :type prompt: str | None
    :param end: Is appended to the end of the user input.
    :type end: str
    :param min_length: The minimum character length the user is allowed to input.
    :type min_length: int | None
    :param max_length: The maximum character length the user is allowed to input.
    :type max_length: int | None
    :param character_whitelist: The user must only use these characters.
    :type character_whitelist: list[str] | None
    :param character_blacklist: The user shouldn't use these characters.
    :type character_blacklist: list[str] | None
    :param fallback_if_blank: The string to be returned if the user doesn't input anything, or None to force the user to input something.
    :type fallback_if_blank: str | None
    :param keep_asking_until_valid: Whether to keep asking the user repeatedly until a valid response is entered.
    :type keep_asking_until_valid: bool
    :return: The text inputted by the user (or None if the user entered an invalid value).
    :rtype: str | None
    """
    printed_text_before_input: str = _printed_text
    while True:

        # ask user
        if prompt is not None:
            print(prompt)
        user_input: str = input()

        # return fallback if blank
        if user_input == '' and fallback_if_blank is not None:
            return fallback_if_blank

        # validate input
        input_is_valid: bool = True
        invalid_reasons: list[str] = []
        if min_length is not None:
            if len(user_input) < min_length:
                input_is_valid = False
                invalid_reasons.append(f'Must be {min_length} characters or more!')
        if max_length is not None:
            if len(user_input) > max_length:
                input_is_valid = False
                invalid_reasons.append(f'Must be {max_length} characters or less!')
        if character_whitelist is not None:
            conforms_to_whitelist: bool = True
            for c in user_input:
                if c not in character_whitelist:
                    conforms_to_whitelist = False
                    break
            if not conforms_to_whitelist:
                input_is_valid = False
                invalid_reasons.append(f'Must only contain these characters: {"".join(character_whitelist)}')
        if character_blacklist is not None:
            conforms_to_blacklist: bool = True
            for c in user_input:
                if c in character_blacklist:
                    conforms_to_blacklist = False
                    break
            if not conforms_to_blacklist:
                input_is_valid = False
                invalid_reasons.append(f'Cannot contain these characters: {"".join(character_blacklist)}')

        # tell the user if their input is invalid
        if not input_is_valid:
            print('Invalid input:', format=ANSI.RED)
            for reason in invalid_reasons:
                print(f'   {reason}', format=ANSI.RED)

        # print the ending
        print_raw(end)

        # exit the loop conditionally
        if input_is_valid or not keep_asking_until_valid:
            break

        # if loop will continue, handle text resetting
        wait_for_enter()
        reprint(printed_text_before_input)

    # return
    if input_is_valid:
        return user_input
    return None

def number_input(prompt: str | None = None, end: str = '\n', must_be_int: bool = False, min_value: float | None = None, max_value: float | None = None, whitelist: list[float] | None = None, blacklist: list[float] | None = None, fallback_if_blank: float | None = None, keep_asking_until_valid: bool = False) -> float | None:
    """
    Prompts the user for a text input.

    :param prompt: The title of the input to be displayed to the user.
    :type prompt: str | None
    :param end: Is appended to the end of the user input.
    :type end: str
    :param must_be_int: Whether the value should be an integer.
    :type must_be_int: bool
    :param min_value: The minimum value the user is allowed to input.
    :type min_value: float | None
    :param max_value: The maximum value the user is allowed to input.
    :type max_value: float | None
    :param whitelist: The user must only use one of these values.
    :type whitelist: list[float] | None
    :param blacklist: The user shouldn't use any of these values.
    :type blacklist: list[float] | None
    :param fallback_if_blank: The string to be returned if the user doesn't input anything, or None to force the user to input something.
    :type fallback_if_blank: float | None
    :param keep_asking_until_valid: Whether to keep asking the user repeatedly until a valid response is entered.
    :type keep_asking_until_valid: bool
    :return: The text inputted by the user (or None if the user entered an invalid value).
    :rtype: str | None
    """
    printed_text_before_input: str = _printed_text
    while True:

        # ask user
        if prompt is not None:
            print(prompt)
        user_input: str = input()

        # return fallback if blank
        if user_input == '' and fallback_if_blank is not None:
            return fallback_if_blank

        # validate input
        input_is_valid: bool = True
        invalid_reasons: list[str] = []
        user_input_number: float = 0
        try:
            user_input_number = float(user_input)
        except ValueError:
            input_is_valid = False
            invalid_reasons.append('Invalid number format!')
        else:
            if must_be_int:
                if user_input_number != round(user_input_number):
                    input_is_valid = False
                    invalid_reasons.append('Must be a whole number!')
                else:
                    user_input_number = int(user_input_number)
            if min_value is not None:
                if user_input_number < min_value:
                    input_is_valid = False
                    invalid_reasons.append(f'Must be {min_value} or more!')
            if max_value is not None:
                if user_input_number > max_value:
                    input_is_valid = False
                    invalid_reasons.append(f'Must be {max_value} or less!')
            if whitelist is not None:
                conforms_to_whitelist: bool = False
                for n in whitelist:
                    if user_input_number == n:
                        conforms_to_whitelist = True
                        break
                if not conforms_to_whitelist:
                    input_is_valid = False
                    invalid_reasons.append(f'Must be one of these numbers: {", ".join(str(n) for n in whitelist)}')
            if blacklist is not None:
                conforms_to_blacklist: bool = True
                for n in blacklist:
                    if user_input_number == n:
                        conforms_to_blacklist = False
                        break
                if not conforms_to_blacklist:
                    input_is_valid = False
                    invalid_reasons.append(f'Cannot be any of these numbers: {", ".join(str(n) for n in blacklist)}')

        # tell the user if their input is invalid
        if not input_is_valid:
            print('Invalid input:', format=ANSI.RED)
            for reason in invalid_reasons:
                print(f'   {reason}', format=ANSI.RED)

        # print the ending
        print_raw(end)

        # exit the loop conditionally
        if input_is_valid or not keep_asking_until_valid:
            break

        # if loop will continue, handle text resetting
        wait_for_enter()
        reprint(printed_text_before_input)

    # return
    if input_is_valid:
        return user_input_number
    return None

def get_terminal_size() -> tuple[int, int]:
    """
    Returns the current size of the terminal in characters.

    :return: The size of the terminal in characters; a tuple of width and height.
    :rtype: tuple[int, int]
    """
    # noinspection PyTypeChecker
    return tuple(shutil.get_terminal_size())

# ALIASES

press_enter_to_continue: Callable = wait_for_enter
clear: Callable = clear_screen
cls: Callable = clear_screen
praw: Callable = print_raw
# noinspection SpellCheckingInspection
iraw: Callable = input_raw

# MAIN

def _main():
    set_title('Soup TUI')
    print_title()
    print('This is a test of the Soup TUI module.')
    print()
    wait_for_enter('reprint')
    reprint()
    print()
    name: str = text_input('What is your name?')
    print(f'Hello, {name}!')
    print()
    username: str = text_input('Please enter a username between 3 and 20 characters.', min_length=3, max_length=20, keep_asking_until_valid=True, character_whitelist=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '_', '-'])
    print(f'Your username is: {username}')
    print()
    print('Test progress bar:')
    progress_bar: ProgressBar = ProgressBar(max_progress=21)
    for i in range(21):
        progress_bar.show(i)
        time.sleep(random.randint(300,1500) / 1000)
    progress_bar.finish()
    print()
    press_enter_to_close()

if __name__ == '__main__':
    _main()
