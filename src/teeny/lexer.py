from teeny.token import Token
from teeny.exception import LexicalError
import re

TOKENS = [
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
    ("NUMBER",    r"\d+"),
    ("NAME",      r"[A-Za-z_][A-Za-z0-9_]*"),
]
KEYWORDS = {
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
    "catch": "CATCH"
}
MASTER_RE = re.compile("|".join(f"(?P<{k}>{p})" for k, p in TOKENS))

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
        if kind == "NAME" and lex in KEYWORDS:
            kind = KEYWORDS[lex]
        line = src.count("\n", 0, pos) + 1
        line_start = src.rfind("\n", 0, pos) + 1
        col = pos - line_start + 1
        out.append(Token(kind, lex, line, col))
        pos = mo.end()
    return out