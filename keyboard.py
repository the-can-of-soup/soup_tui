"""
Windows-only tools for reading terminal keyboard input (some wrapped functions from ``msvcrt``).
``msvcrt`` docs: https://docs.python.org/3/library/msvcrt.html
"""

# IMPORTS

import platform

if platform.system() != 'Windows':
    raise OSError('The soup_tui.keyboard module only supports the Windows operating system!')

import msvcrt

# KEY CODES

SPACE: str       = ' '
BACKSPACE: str   = '\b'
TAB: str         = '\t'
ENTER: str       = '\r'
RETURN: str      = '\r'
UP_ARROW: str    = '\xe0H'
DOWN_ARROW: str  = '\xe0P'
LEFT_ARROW: str  = '\xe0K'
RIGHT_ARROW: str = '\xe0M'
F1: str          = '\x00;'
F2: str          = '\x00<'
F3: str          = '\x00='
F4: str          = '\x00>'
F5: str          = '\x00?'
F6: str          = '\x00@'
F7: str          = '\x00A'
F8: str          = '\x00B'
F9: str          = '\x00C'
F10: str         = '\x00D'
# F11 cannot be detected (fullscreen toggle)
F12: str         = '\xe0\x86'
CTRL_A: str      = '\x01'
CTRL_B: str      = '\x02'
# CTRL+C cannot be detected (stops execution)
CTRL_D: str      = '\x04'
CTRL_E: str      = '\x05'
CTRL_F: str      = '\x06'
CTRL_G: str      = '\x07'
CTRL_H: str      = '\x08'
# CTRL+I is indistinguishable from TAB
CTRL_J: str      = '\n'
CTRL_K: str      = '\x0b'
CTRL_L: str      = '\x0c'
# CTRL+M is indistinguishable from ENTER
CTRL_N: str      = '\x0e'
CTRL_O: str      = '\x0f'
CTRL_P: str      = '\x10'
CTRL_Q: str      = '\x11'
CTRL_R: str      = '\x12'
CTRL_S_UNRELIABLE: str = '\x13' # CTRL+S sometimes cannot be detected (pauses execution until a key is pressed)
CTRL_T: str      = '\x14'
CTRL_U: str      = '\x15'
# CTRL+V is indistinguishable from typing what is in the clipboard
CTRL_W: str      = '\x17'
CTRL_X: str      = '\x18'
CTRL_Y: str      = '\x19'
CTRL_Z: str      = '\x2a'
CTRL_2: str      = '\x00\x03'
# No other CTRL+number combinations can be detected
CTRL_UP_ARROW: str = '\xe0\x8d'
CTRL_DOWN_ARROW: str = '\xe0\x91'
CTRL_LEFT_ARROW: str = '\xe0s'
CTRL_RIGHT_ARROW: str = '\xe0t'

# DEFINITIONS

def read_key(blocking: bool = True) -> str | None:
    """
    Reads one keypress.

    :param blocking: If enabled, waits for a keypress. Otherwise, checks if a key was pressed.
    :type blocking: bool
    :return: The pressed key as a 1 or 2-character string. 2-character strings represent special function keys. If blocking is disabled and no key was read, returns ``None`` instead.
    :rtype: str
    """
    # Return None if blocking disabled and no key is waiting to be read
    if not blocking:
        if msvcrt.kbhit() == 0:
            return None

    # Grab the key that was pressed
    first_key: str = msvcrt.getwch()

    # Return the key, unless it is an escape code that signifies a special function key
    if first_key not in ('\x00', '\xe0'):
        return first_key

    # If it was a special function key, read the second part and return the full code
    second_key: str = msvcrt.getwch()
    return first_key + second_key

def dump_cache() -> list[str]:
    """
    Reads keypresses until there are none left to read.

    :return: Every keypress that was read.
    :rtype: list[str]
    """
    cache: list[str] = []
    while (next_key := read_key(False)) is not None:
        cache.append(next_key)
    return cache
