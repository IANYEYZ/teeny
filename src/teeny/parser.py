from teeny.AST import AST
from teeny.token import Token
from teeny.exception import SyntaxError

def infixOperators(op) -> list[int]:
    if op.startswith("<") and op.endswith(">"):
        return [13, 14]
    return {
        '=': [1, 2], ':=': [1, 2], '?=': [1, 2], '+=': [1, 2], '-=': [1, 2], '*=': [1, 2],
        '/=': [1, 2], '%=': [1, 2], '|>': [1, 2],
        '||': [5, 6],
        '&&': [7, 8],
        '==': [9, 10], '!=': [9, 10], '>': [9, 10], '<': [9, 10], '=~': [9, 10], '>=': [9, 10], 
        '<=': [9, 10], '??': [9, 10], '?:': [9, 10],
        '+': [13, 14], '-': [13, 14], '..': [13, 14],
        '*': [15, 16], '/': [15, 16], '%': [15, 16],
        '.': [19, 20]
    }.get(op)

def prefixOperators(op) -> int:
    return {
        '+': 15, '-': 15, '!': 15, '%': 15, "...": 15
    }.get(op)

def suffixOperators(op) -> int:
    return {
        '!': 17, '[': 17, '(': 17
    }.get(op)

def advance(tokens: list[Token], p: int, expectedTyp: str | list[str]) -> int:
    if not isinstance(expectedTyp, list):
        expectedTyp = [expectedTyp]
    for typ in expectedTyp:
        if tokens[p].typ == typ: break
    else:
        raise SyntaxError(f"Unexpected token: found {tokens[p].value}, except {expectedTyp}"
                        , tokens[p].line, tokens[p].col)
    return p + 1

def parse(tokens: list[Token], p = 0, minBp = 0) -> list[AST | int]:
    while p < len(tokens) and tokens[p].typ == "SEMI": p += 1
    if p == len(tokens): return [None, p]
    lhs = None
    if tokens[p].typ == "NUMBER" or tokens[p].typ == "NAME":
        if p + 1 < len(tokens) and (tokens[p + 1].typ == "ARROW" or tokens[p + 1].typ == "AT"):
            name = tokens[p]
            p = advance(tokens, p, "NAME")
            isDynamic = False
            if tokens[p].typ == "AT":
                p = advance(tokens, p, "AT")
                isDynamic = True
            p = advance(tokens, p, "ARROW")
            rhs, p = parse(tokens, p, 0)
            lhs = AST("FN" if not isDynamic else "FN-DYNAMIC", [rhs], [name])
        else:
            lhs = AST("NUMBER" 
                      if tokens[p].typ == "NUMBER" 
                      else "NAME", [], tokens[p].value)
            p += 1
    elif tokens[p].typ == "STRING":
        children = []
        while p < len(tokens) and (tokens[p].typ == "STRING" or tokens[p].typ == "INTE_START"):
            if tokens[p].typ == "INTE_START":
                p = advance(tokens, p, "INTE_START")
                lhs, p = parse(tokens, p, 0)
                children.append(lhs)
                p = advance(tokens, p, "INTE_END")
            else:
                children.append(AST("STRING", [], tokens[p].value))
                p += 1
        lhs = AST("STRING", children)
    elif tokens[p].typ == "REGEX":
        lhs = AST("REGEX", [], tokens[p].value[1:-1])
        p += 1
    elif tokens[p].typ == "LPAREN":
        p = advance(tokens, p, "LPAREN")
        nowPos = p
        res = 1
        p -= 1
        while res:
            p += 1
            if tokens[p].typ == "RPAREN":
                res -= 1
            elif tokens[p].typ == "LPAREN":
                res += 1
        p = advance(tokens, p, "RPAREN")
        if p < len(tokens) and (tokens[p].typ == "ARROW" or tokens[p].typ == "AT"):
            p = nowPos
            params = []
            while tokens[p].typ != "RPAREN":
                rhs, p = parse(tokens, p, 0)
                if rhs.value == "=":
                    params.append([rhs.children[0], rhs.children[1]])
                elif rhs.value == "...":
                    params.append([rhs.children[0]])
                else:
                    params.append(rhs)
                if tokens[p].typ == "COMMA": p += 1
            p = advance(tokens, p, "RPAREN")
            isDynamic = False
            if tokens[p].typ == "AT":
                p = advance(tokens, p, "AT")
                isDynamic = True
            p = advance(tokens, p, "ARROW")
            rhs, p = parse(tokens, p, 0)
            children = [rhs]
            lhs = AST("FN" if not isDynamic else "FN-DYNAMIC", children, params)
        else:
            p = nowPos
            lhs, p = parse(tokens, p, 0)
            p = advance(tokens, p, "RPAREN")
    elif tokens[p].typ == "LSHPAREN":
        p = advance(tokens, p, "LSHPAREN")
        children = []
        while tokens[p].typ != "RSHPAREN":
            rhs, p = parse(tokens, p, 0)
            children.append(rhs)
        lhs = AST("BLOCK", children)
        p = advance(tokens, p, "RSHPAREN")
    elif tokens[p].typ == "LSQPAREN":
        p = advance(tokens, p, "LSQPAREN")
        children = []
        while tokens[p].typ != "RSQPAREN":
            if tokens[p].typ == "COLON":
                p = advance(tokens, p, "COLON")
                rhs, p = parse(tokens, p, 0)
                children.append(AST("PAIR", [rhs]))
                if tokens[p].typ == "COMMA": p += 1
                continue
            rhs, p = parse(tokens, p, 0)
            children.append(rhs)
            if tokens[p].typ == "COMMA": p = advance(tokens, p, "COMMA")
            elif tokens[p].typ == "COLON":
                p += 1
                rhs, p = parse(tokens, p, 0)
                lhs = children.pop()
                children.append(AST("PAIR", [lhs, rhs]))
                if tokens[p].typ == "COMMA": p += 1
        lhs = AST("TABLE", children)
        p = advance(tokens, p, "RSQPAREN")
    elif tokens[p].typ == "IF":
        p = advance(tokens, p, "IF")
        lhs, p = parse(tokens, p, 0)
        rhs, p = parse(tokens, p, 0)
        children = [rhs]
        if p >= len(tokens) or (tokens[p].typ != "ELSE" and tokens[p].typ != "ELIF"):
            lhs = AST("IF", [lhs, *children])
        else:
            while p < len(tokens) and (tokens[p].typ == "ELSE" or tokens[p].typ == "ELIF"):
                if tokens[p].typ == "ELSE":
                    p = advance(tokens, p, "ELSE")
                    rhs, p = parse(tokens, p, 0)
                    children_ = [rhs]
                    rhs = AST("ELSE", children_)
                    children.append(rhs)
                else:
                    p = advance(tokens, p, "ELIF")
                    expr, p = parse(tokens, p, 0)
                    rhs, p = parse(tokens, p, 0)
                    rhs = AST("ELIF", [expr, rhs])
                    children.append(rhs)
            lhs = AST("IF", [lhs, *children])
    elif tokens[p].typ == "WHILE":
        p = advance(tokens, p, "WHILE")
        lhs, p = parse(tokens, p, 0)
        rhs, p = parse(tokens, p, 0)
        lhs = AST("WHILE", [lhs, rhs])
    elif tokens[p].typ == "FOR":
        p = advance(tokens, p, "FOR")
        lhs, p = parse(tokens, p, 0)
        p = advance(tokens, p, "IN")
        rhs, p = parse(tokens, p, 0)
        body, p = parse(tokens, p, 0)
        lhs = AST("FOR", [lhs, rhs, body])
    elif tokens[p].typ == "MATCH":
        p = advance(tokens, p, "MATCH")
        lhs, p = parse(tokens, p, 0)
        if tokens[p].typ == "AS":
            p = advance(tokens, p, "AS")
            rhs, p = parse(tokens, p, 0)
            lhs = [lhs, rhs]
        p = advance(tokens, p, "LSHPAREN")
        children = []
        while tokens[p].typ != "RSHPAREN":
            rhs, p = parse(tokens, p, 0)
            p = advance(tokens, p, 'COLON')
            tr, p = parse(tokens, p, 0)
            children.append(AST("OPT", [rhs, tr]))
            if tokens[p].typ == "COMMA":
                p = advance(tokens, p, "COMMA")
        lhs = AST("MATCH", children, lhs)
        p = advance(tokens, p, "RSHPAREN")
    elif tokens[p].typ == "TRY":
        p = advance(tokens, p, "TRY")
        lhs, p = parse(tokens, p, 0)
        p = advance(tokens, p, "CATCH")
        rhs, p = parse(tokens, p, 0)
        lhs = AST("TRY", [lhs, rhs])
    elif tokens[p].typ == "FN":
        isDynamic = False
        p = advance(tokens, p, "FN")
        if tokens[p].typ == "AT":
            p = advance(tokens, p, "AT")
            isDynamic = True
        p = advance(tokens, p, "LPAREN")
        params = []
        while tokens[p].typ != "RPAREN":
            rhs, p = parse(tokens, p, 0)
            if rhs.value == "=":
                params.append([rhs.children[0], rhs.children[1]])
            elif rhs.value == "...":
                params.append([rhs.children[0]])
            else:
                params.append(rhs)
            if tokens[p].typ == "COMMA": p += 1
        p = advance(tokens, p, "RPAREN")
        if isDynamic:
            rhs, p = parse(tokens, p, 0)
            children = [rhs]
            lhs = AST("FN-DYNAMIC", children, params)
        else:
            rhs, p = parse(tokens, p, 0)
            children = [rhs]
            lhs = AST("FN", children, params)
    elif tokens[p].typ == "RETURN":
        p = advance(tokens, p, "RETURN")
        lhs, p = parse(tokens, p, 0)
        lhs = AST("RETURN", [lhs])
    elif tokens[p].typ == "BREAK":
        p = advance(tokens, p, "BREAK")
        lhs, p = parse(tokens, p, 0)
        if lhs == None:
            lhs = AST("BREAK", [])
        else:
            lhs = AST("BREAK", [lhs])
    elif tokens[p].typ == "CONTINUE":
        p = advance(tokens, p, "CONTINUE")
        lhs, p = parse(tokens, p, 0)
        if lhs == None:
            lhs = AST("CONTINUE", [])
        else:
            lhs = AST("CONTINUE", [lhs])
    else:
        op = tokens[p].value
        rBp = prefixOperators(op)
        if rBp == None:
            return [None, p]
        p += 1
        rhs, p = parse(tokens, p, rBp)
        lhs = AST("PREOP", [rhs], op)
    while True:
        if p == len(tokens): break
        op = tokens[p] if p < len(tokens) else None
        if op == None: break
        if op.typ == "NAME" or op.typ == "NUMBER" or op.typ == "STRING" \
            or op.typ == "RPAREN" or op.typ == "RSQPAREN" or op.typ == "RSHPAREN" or op.typ == "LSHPAREN" \
            or op.typ == "COMMA" or op.typ == "COLON" or op.typ == "IF" or op.typ == "FN" \
            or op.typ == "WHILE" or op.typ == "THEN" or op.typ == "END" or op.typ == "ELSE" \
            or op.typ == "TRY" or op.typ == "CATCH" or op.typ == "ELIF" or op.typ == "FOR" \
            or op.typ == "IN" or op.typ == "SEMI" or op.typ == "MATCH" or op.typ == "INTE_END"\
            or op.typ == "AS" or op.typ == "RETURN" or op.typ == "BREAK" or op.typ == "CONTINUE":
            break
        op = op.value

        if suffixOperators(op) != None:
            lBp = suffixOperators(op)
            if lBp < minBp: break
            p += 1
            if op == '[':
                rhs, p = parse(tokens, p, 0)
                p += 1
                lhs = AST("OP", [lhs, rhs], "[]")
            elif op == '(':
                children = []
                while tokens[p].typ != "RPAREN":
                    rhs, p = parse(tokens, p, 0)
                    if rhs.value == "=":
                        rhs = AST("KWARG", [rhs.children[0], rhs.children[1]])
                    if tokens[p].typ == "COMMA": p += 1
                    children.append(rhs)
                p += 1
                lhs = AST("CALL", [lhs, *children])
            else:
                lhs = AST("SUFOP", [lhs], op)
            continue
        lBp, rBp = infixOperators(op)
        if lBp < minBp: break
        p += 1
        rhs, p = parse(tokens, p, rBp)

        lhs = AST("OP", [lhs, rhs], op)
    return [lhs, p]