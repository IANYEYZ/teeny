from teeny.token import Token
from teeny.exception import LexicalError
import re

TOKENS: list[tuple[str, str]] = [
    ("WS",        r"[ \t\r\n]+"),
    ("COMMENT",   r"#.*"),
    ("DEFINE",    r":="),
    ("EQEQ",      r"=="),
    ("NEQ",       r"!="),
    ("GEQ",       r">="),
    ("LEQ",       r"<="),
    ("GT",        r">"),
    ("LT",        r"<"),
    ("ANDAND",    r"&&"),
    ("OROR",      r"\|\|"),
    ("NOT",       r"\!"),
    ("PIPE",      r"\|>"),
    ("ARROW",     r"=>"),
    ("ASSIGN",    r"="),
    ("DEFASSIGN", r"\?\="),
    ("QEQE",      r"\?\?"),
    ("QECOLON",   r"\?\:"),
    ("SPREAD",    r"\.\.\."),
    ("RNGLI",     r"\.\."),
    ("PLUS",      r"\+"),
    ("MINUS",     r"-"),
    ("STAR",      r"\*"),
    ("SLASH",     r"/"),
    ("MOD",       r"%"),
    ("LPAREN",    r"\("),
    ("RPAREN",    r"\)"),
    ("SEMI",      r";"),
    ("COLON",     r":"),
    ("COMMA",     r","),
    ("DOT",       r"\."),
    ("LSQPAREN",  r"\["),
    ("RSQPAREN",  r"\]"),
    ("LSHPAREN",  r"\{"),
    ("RSHPAREN",  r"\}"),
    ("AT",        r"@"),
    ("STRING",    r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\''),
    ("NUMBER", r"(?:\d+\.(?![A-Za-z_]|\.)(?:\d*)|\.\d+|\d+)(?:[eE][+-]?\d+)?"),
    ("NAME",      r"[A-Za-z_][A-Za-z0-9_]*"),
]
KEYWORDS: dict[str: str] = {
    "if": "IF",
    "then": "THEN",
    "else": "ELSE",
    "elif": "ELIF",
    "fn": "FN",
    "while": "WHILE",
    "for": "FOR",
    "in": "IN",
    "match": "MATCH",
    "try": "TRY",
    "catch": "CATCH",
    "as": "AS"
}
MASTER_RE: re.Pattern = re.compile("|".join(f"(?P<{k}>{p})" for k, p in TOKENS))

def findMatchingRightParen(src: str, pos: int):
    res = 1; pos = pos + 1
    flag = False
    while pos < len(src) and res:
        if src[pos] == "}" and not flag: res -= 1
        elif src[pos] == "{" and not flag: res += 1
        if src[pos] == "\\": flag = True
        else: flag = False
        pos += 1
    return pos

def parseString(src: str, pos: int, quoteChar: str):
    pos += 1
    now = ""
    res = []
    flag = False
    while src[pos] != quoteChar:
        if src[pos] == "{" and not flag:
            res.append(Token("STRING", now, 0, 0))
            now = ""
            res.append(Token("INTE_START", "", 0, 0))
            ed = findMatchingRightParen(src, pos)
            tokens = tokenize(src[pos + 1:ed - 1])
            res.extend(tokens)
            res.append(Token("INTE_END", "", 0, 0))
            pos = ed
        else:
            if src[pos] == "\\": flag = True
            else: flag = False
            now += src[pos]
            pos = pos + 1
    if now != "": res.append(Token("STRING", now, 0, 0))
    return res

def tokenize(src: str) -> list[Token]:
    pos = 0
    line = 0
    out = []
    m = MASTER_RE.match
    n = len(src)
    while pos < n:
        mo = m(src, pos)
        if not mo:
            line = src.count("\n", 0, pos) + 1
            line_start = src.rfind("\n", 0, pos) + 1
            col = pos - line_start + 1
            snippet = src[pos : pos + 20].splitlines()[0]
            raise LexicalError(f"Unknown Character {src[pos]}", line, col)
        kind = mo.lastgroup
        lex = mo.group()
        if kind in ("WS", "COMMENT"):
            pos = mo.end()
            continue
        if kind == "STRING":
            quoteCharacter = lex[0]
            out.extend(parseString(src, pos, quoteCharacter))
            pos = mo.end()
            continue
        if kind == "NAME" and lex in KEYWORDS:
            kind = KEYWORDS[lex]
        line = src.count("\n", 0, pos) + 1
        line_start = src.rfind("\n", 0, pos) + 1
        col = pos - line_start + 1
        out.append(Token(kind, lex, line, col))
        pos = mo.end()
    return out