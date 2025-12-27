from teeny.token import Token
from teeny.exception import LexicalError
import re

TOKENS: list[tuple[str, str]] = [
    # whitespace & comment
    ("WS",          r"[ \t\r\n]+"),
    ("COMMENT",     r"#[^\n]*"),

    # multi-character operators (MUST come before shorter ones)
    ("DEFINE",      r":="),
    ("EQEQ",        r"=="),
    ("NEQ",         r"!="),
    ("GEQ",         r">="),
    ("LEQ",         r"<="),
    ("MEQ",         r"=~"),
    ("ANDAND",      r"&&"),
    ("OROR",        r"\|\|"),
    ("PIPE",        r"\|>"),
    ("ARROW",       r"=>"),

    ("DEFASSIGN",   r"\?\="),
    ("QEQE",        r"\?\?"),
    ("QECOLON",     r"\?\:"),

    ("SPREAD",      r"\.\.\."),   # must be before RNGLI
    ("RNGLI",       r"\.\."),     # must be before DOT

    # single-character operators
    ("PLUS",        r"\+"),
    ("MINUS",       r"-"),
    ("STAR",        r"\*"),
    ("SLASH",       r"/"),
    ("MOD",         r"%"),
    ("GT",          r">"),
    ("LT",          r"<"),
    ("ASSIGN",      r"="),
    ("NOT",         r"!"),

    ("COLON",       r":"),
    ("COMMA",       r","),
    ("DOT",         r"\."),

    # grouping
    ("LPAREN",      r"\("),
    ("RPAREN",      r"\)"),
    ("LSQPAREN",    r"\["),
    ("RSQPAREN",    r"\]"),
    ("LSHPAREN",    r"\{"),
    ("RSHPAREN",    r"\}"),

    ("SEMI",        r";"),
    ("AT",          r"@"),

    # literals
    ("REGEX",       r"`(?:\\.|[^`\\])*`"),

    ("STRING",      r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\''),

    ("NUMBER",      r"(?:\d+\.(?![A-Za-z_]|\.)(?:\d*)|\.\d+|\d+)(?:[eE][+-]?\d+)?"),

    ("NAME",        r"[A-Za-z_][A-Za-z0-9_]*"),
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
    "as": "AS",
    "return": "RETURN",
    "break": "BREAK",
    "continue": "CONTINUE"
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

def escapeString(s: str) -> str:
    inner = s  # remove quotes
    result = []
    i = 0
    while i < len(inner):
        if inner[i] == "\\" and i + 1 < len(inner):
            nxt = inner[i + 1]
            if nxt == "n": result.append("\n"); i += 2; continue
            if nxt == "t": result.append("\t"); i += 2; continue
            if nxt == "\\": result.append("\\"); i += 2; continue
            if nxt == '"': result.append('"'); i += 2; continue
            if nxt == '\'': result.append('\''); i += 2; continue
            # leave unknown escapes untouched
        result.append(inner[i]); i += 1
    return "".join(result)
def parseString(src: str, pos: int, quoteChar: str):
    pos += 1
    now = ""
    res = []
    flag = False
    if src[pos] == quoteChar:
        res.append(Token("STRING", "", 0, 0))
        return res
    while src[pos] != quoteChar:
        if src[pos] == "{" and not flag:
            res.append(Token("STRING", escapeString(now), 0, 0))
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
    if now != "": res.append(Token("STRING", escapeString(now), 0, 0))
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