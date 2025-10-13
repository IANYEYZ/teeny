from teeny.AST import AST
from teeny.token import Token
from teeny.exception import SyntaxError

def infixOperators(op) -> list[int]:
    return {
        '=': [1, 2], ':=': [1, 2],
        '||': [5, 6],
        '&&': [7, 8],
        '==': [9, 10], '!=': [9, 10], '>': [9, 10], '<': [9, 10], '>=': [9, 10], '<=': [9, 10],
        '+': [11, 12], '-': [11, 12],
        '*': [13, 14], '/': [13, 14], '%': [13, 14],
        '.': [20, 19]
    }[op]

def prefixOperators(op) -> int:
    return {
        '+': 15, '-': 15, '!': 15, '%': 15
    }[op]

def suffixOperators(op) -> int:
    return {
        '!': 17, '[': 17, '(': 17
    }.get(op)

def advance(tokens: list[Token], p: int, expectedTyp: str):
    if tokens[p].typ == expectedTyp: return p + 1
    else:
        raise SyntaxError(f"Unexpected token: found {tokens[p].value}, except {expectedTyp}"
                          , tokens[p].line, tokens[p].col)

def parse(tokens: list[Token], p = 0, minBp = 0) -> list[AST | int]:
    while tokens[p].typ == "SEMI": p += 1
    lhs = None
    if tokens[p].typ == "NUMBER" or tokens[p].typ == "NAME" or tokens[p].typ == "STRING":
        lhs = AST("NUMBER" 
                  if tokens[p].typ == "NUMBER" 
                  else ("NAME" if tokens[p].typ == "NAME" else "STRING"), [], tokens[p].value)
        p += 1
    elif tokens[p].typ == "LPAREN":
        p = advance(tokens, p, "LPAREN")
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
            rhs, p = parse(tokens, p, 0)
            children.append(rhs)
            if tokens[p].typ == "COMMA": p += 1
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
        if p >= len(tokens) or tokens[p].typ != "ELSE":
            lhs = AST("IF", [lhs, *children])
        else:
            p = advance(tokens, p, "ELSE")
            rhs, p = parse(tokens, p, 0)
            children_ = [rhs]
            rhs = AST("ELSE", children_)
            lhs = AST("IF", [lhs, *children, rhs])
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
    elif tokens[p].typ == "FN":
        isDynamic = False
        p = advance(tokens, p, "FN")
        if tokens[p].typ == "AT":
            p = advance(tokens, p, "AT")
            isDynamic = True
        p = advance(tokens, p, "LPAREN")
        params = []
        while tokens[p].typ != "RPAREN":
            params.append(tokens[p].value)
            p += 1
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
    else:
        op = tokens[p].value
        rBp = prefixOperators(op)
        p += 1
        rhs, p = parse(tokens, p, rBp)
        lhs = AST("PREOP", [rhs], op)
    while True:
        op = tokens[p] if p < len(tokens) else None
        if op == None: break
        if op.typ == "NAME" or op.typ == "NUMBER" or op.typ == "STRING" \
            or op.typ == "RPAREN" or op.typ == "RSQPAREN" or op.typ == "RSHPAREN" or op.typ == "LSHPAREN" \
            or op.typ == "COMMA" or op.typ == "COLON" or op.typ == "IF" or op.typ == "FN" \
            or op.typ == "WHILE" or op.typ == "THEN" or op.typ == "END" or op.typ == "ELSE" \
            or op.typ == "FOR" or op.typ == "IN" or op.typ == "SEMI":
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
                    children.append(rhs)
                    if tokens[p].typ == "COMMA": p += 1
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