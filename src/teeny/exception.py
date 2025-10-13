from typing import Optional


class TeenyError(Exception):
    pass

class LexicalError(TeenyError):
    def __init__(self, message: str, line: int, col: int):
        self.message = message
        self.line = line
        self.col = col

    def __str__(self):
        loc = f"line {self.line}, column {self.col}"
        return f"""Lexical Error at {loc}:
{self.message}"""

class SyntaxError(TeenyError):
    def __init__(self, message: str, line: int, col: int, hint: Optional[str] = None):
        self.message = message
        self.line = line
        self.col = col
        self.hint = hint

    def __str__(self):
        loc = f"line {self.line}, column {self.col}"
        return f"""Syntax Error at {loc}:
{self.message}""" + ("\nDid you forget " + self.hint if self.hint != None else "")

class RuntimeError(TeenyError):
    def __init__(self, message: str):
        self.message = message
    
    def __str__(self):
        return f"""Runtime Error:
{self.message}"""