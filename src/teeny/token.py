from dataclasses import dataclass

@dataclass(repr = True)
class Token:
    typ: str
    value: str
    line: int
    col: int