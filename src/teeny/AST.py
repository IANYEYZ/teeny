from typing import Any

def toString(value: Any) -> str:
    if isinstance(value, list):
        return "[" + ", ".join([toString(v) for v in value]) + "]"
    return str(value)

class AST:
    def __init__(self, typ: str, children: list["AST"] = [], value: any = None) -> None:
        self.typ = typ; self.children = children; self.value = value
    def toString(self, tab: int = 0) -> str:
        res = ""
        res += "    " * tab + self.typ + ' ' + (toString(self.value) if self.value != None else "") + '\n'
        for c in self.children:
            res += c.toString(tab + 1)
        return res
    def __repr__(self) -> str:
        return self.toString()