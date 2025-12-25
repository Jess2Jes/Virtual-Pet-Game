"""
This module provides utility functions for colorizing text output in the console, it is a wrapper around the colorama library.
"""
from colorama import Fore

def reset_color(text: str) -> str:
    """
    Reset console color.

    Example usage:
        print(reset_color("text"))
    """
    return f"{Fore.RESET}{text}{Fore.RESET}"

def red(text: str) -> str:
    """
    Wrap text in ANSI red foreground color.

    Args:
        text: The text to colorize.

    Returns:
        The text wrapped with red color codes.
    """
    return f"{Fore.RED}{text}{Fore.RESET}"


def green(text: str) -> str:
    """
    Wrap text in ANSI green foreground color.

    Args:
        text: The text to colorize.

    Returns:
        The text wrapped with green color codes.
    """
    return f"{Fore.GREEN}{text}{Fore.RESET}"


def blue(text: str) -> str:
    """
    Wrap text in ANSI blue foreground color.

    Args:
        text: The text to colorize.

    Returns:
        The text wrapped with blue color codes.
    """
    return f"{Fore.BLUE}{text}{Fore.RESET}"


def yellow(text: str) -> str:
    """
    Wrap text in ANSI yellow foreground color.

    Args:
        text: The text to colorize.

    Returns:
        The text wrapped with yellow color codes.
    """
    return f"{Fore.YELLOW}{text}{Fore.RESET}"


def cyan(text: str) -> str:
    """
    Wrap text in ANSI cyan foreground color.

    Args:
        text: The text to colorize.

    Returns:
        The text wrapped with cyan color codes.
    """
    return f"{Fore.CYAN}{text}{Fore.RESET}"


def magenta(text: str) -> str:
    """
    Wrap text in ANSI magenta foreground color.

    Args:
        text: The text to colorize.

    Returns:
        The text wrapped with magenta color codes.
    """
    return f"{Fore.MAGENTA}{text}{Fore.RESET}"
