from teeny.AST import AST
from teeny.value import Value, Number, String, Table, Closure, Nil, Env, Error, ValError, BuiltinClosure, snapshot, isTruthy
from teeny.glob import makeGlobal
from teeny.exception import RuntimeError

def assignVariable(lhs: AST, rhs: Value, env: Env, isDeclare: bool = False):
    if lhs.typ != "TABLE":
        if lhs.typ == "NAME":
            if isDeclare:
                env.define(lhs.value, rhs)
            else:
                env.write(lhs.value, rhs)
        elif lhs.value == ".":
            l = interpret(lhs.children[0], env)
            r = String(value = lhs.children[1].value)
            if isDeclare:
                l.define(r, rhs)
            else:
                l.set(r, rhs)
        elif lhs.value == "[]":
            l = interpret(lhs.children[0], env)
            r = interpret(lhs.children[1], env)
            if isDeclare:
                l.define(r, rhs)
            else:
                l.set(r, rhs)
    else:
        cnt: int = 0
        for c in lhs.children:
            if c.typ == "PAIR":
                assignVariable(c.children[1], rhs.get(String(value = c.children[0].value)), env, isDeclare)
            elif c.typ == "NAME" and not isinstance(rhs.get(String(value = c.value)), Nil):
                assignVariable(c, rhs.get(String(value = c.value)), env, isDeclare)
            else:
                assignVariable(c, rhs.get(Number(value = cnt)), env, isDeclare)
                cnt += 1

def interpret(ast: AST, env: Env = makeGlobal()) -> Value:
    if ast.typ == "NUMBER":
        return Number(value = int(ast.value))
    if ast.typ == "STRING":
        return String(value = str(ast.value)[1:-1])
    elif ast.typ == "NAME":
        if ast.value == "nil":
            return Nil()
        return env.read(ast.value)
    elif ast.typ == "TABLE":
        value = Table({})
        for c in ast.children:
            if c.typ == "PAIR":
                # c.children[0] is guareenteed a NAME or a VALUE
                if c.children[0].typ == "NAME":
                    val = interpret(c.children[1], env)
                    if isinstance(val, Error): return val
                    value.update({String(value = c.children[0].value): val})
                else:
                    key = interpret(c.children[0], env)
                    if isinstance(key, Error): return key
                    val = interpret(c.children[1], env)
                    if isinstance(val, Error): return val
                    value.update({val: val})
            else:
                val = interpret(c, env)
                if isinstance(val, Error): return val
                value.append(val)
        return value
    elif ast.typ == "FN":
        value = Closure(ast.value, ast.children, Env(outer = env), False)
        return value
    elif ast.typ == "FN-DYNAMIC":
        value = Closure(ast.value, ast.children, Env(outer = env), True)
        return value
    elif ast.typ == "CALL":
        value = interpret(ast.children[0], env)
        if isinstance(value, Error): return value
        params = ast.children[1:]
        for pos, p in enumerate(params):
            val = interpret(p, env)
            if isinstance(val, Error): return val
            params[pos] = interpret(p, env)
        if isinstance(value, BuiltinClosure):
            if value.hasEnv:
                return value([*params, env])
        return value(params)
    elif ast.typ == "IF":
        value = interpret(ast.children[0], env)
        if isinstance(value, Error): return value
        if isTruthy(value):
            return interpret(ast.children[1])
        for c in ast.children[2:]:
            if c.typ == "ELIF":
                value = interpret(c.children[0], env)
                if isinstance(value, Error): return value
                if isTruthy(value):
                    return interpret(c.children[1], env)
        if ast.children[-1].typ == "ELSE":
            return interpret(ast.children[-1].children[0])
        return Nil()
    elif ast.typ == "WHILE":
        res = Nil()
        val = interpret(ast.children[0], env)
        if isinstance(val, Error): return val
        while isTruthy(val):
            res = interpret(ast.children[1])
            if isinstance(res, Error): return res
            val = interpret(ast.children[0], env)
            if isinstance(val, Error): return val
        return res
    elif ast.typ == "FOR":
        lhs = ast.children[0]
        rhs = interpret(ast.children[1])
        if isinstance(rhs, Error): return rhs
        if not isinstance(rhs, Table):
            raise RuntimeError("Only Table is iterrable")
        curEnv = snapshot(env)
        lst = Table()
        st = rhs.get(String(value = "_iter_"))([])
        v = st()
        while not isinstance(v, Nil):
            p = v
            env = snapshot(curEnv)
            assignVariable(lhs, rhs.get(Number(value = p)), env, True)
            val = interpret(ast.children[2], env)
            if isinstance(val, Error): return val
            lst.append(val)
            v = st()
        env = snapshot(curEnv)
        return lst
    elif ast.typ == "BLOCK":
        lst = Nil()
        nEnv = Env(env)
        for b in ast.children:
            lst = interpret(b, nEnv)
            if isinstance(lst, Error): return lst
        return lst
    elif ast.typ == "MATCH":
        val = interpret(ast.value, env)
        if isinstance(val, Error): return val
        nEnv = Env(env)
        for c in ast.children:
            if c.typ != "OPT":
                raise RuntimeError("OPT is the only type allowed inside a match expression")
            lft = interpret(c.children[0], nEnv) if c.children[0].value != '_' else Number(1)
            if isinstance(lft, Error): return lft
            if isTruthy(lft == val):
                return interpret(c.children[1], nEnv)
        return Nil()
    elif ast.typ == "TRY":
        val = interpret(ast.children[0], env)
        if isinstance(val, Error):
            rhs = interpret(ast.children[1], env)
            if not isinstance(rhs, (Closure, BuiltinClosure, Table)):
                raise RuntimeError("catch expression must be callable")
            return rhs([ValError(typ = val.typ, value = val.value)], True)
        else:
            return val
    elif ast.typ == "OP":
        if ast.value == "+":
            return interpret(ast.children[0], env) + interpret(ast.children[1], env)
        if ast.value == "-":
            return interpret(ast.children[0], env) - interpret(ast.children[1], env)
        if ast.value == "*":
            return interpret(ast.children[0], env) * interpret(ast.children[1], env)
        if ast.value == "/":
            return interpret(ast.children[0], env) / interpret(ast.children[1], env)
        if ast.value == "%":
            return interpret(ast.children[0], env) % interpret(ast.children[1], env)
        if ast.value == "&&":
            return interpret(ast.children[0], env) and interpret(ast.children[1], env)
        if ast.value == "||":
            return interpret(ast.children[0], env) or interpret(ast.children[1], env)
        if ast.value == "==":
            return interpret(ast.children[0], env) == interpret(ast.children[1], env)
        if ast.value == "!=":
            return interpret(ast.children[0], env) != interpret(ast.children[1], env)
        if ast.value == ">":
            return interpret(ast.children[0], env) > interpret(ast.children[1], env)
        if ast.value == "<":
            return interpret(ast.children[0], env) < interpret(ast.children[1], env)
        if ast.value == ">=":
            return interpret(ast.children[0], env) >= interpret(ast.children[1], env)
        if ast.value == "<=":
            return interpret(ast.children[0], env) <= interpret(ast.children[1], env)
        if ast.value == ":=":
            # The left is guarenteed a name or a Table
            val = interpret(ast.children[1], env)
            if isinstance(val, Error): return val
            assignVariable(ast.children[0], val, env, True)
            return val
        if ast.value == "=":
            # The left is guarenteed a name or a Table
            val = interpret(ast.children[1], env)
            if isinstance(val, Error): return val
            assignVariable(ast.children[0], val, env, False)
            return val
        if ast.value == ".":
            lhs = interpret(ast.children[0], env)
            if isinstance(lhs, Error): return lhs
            return lhs.get(String(value = ast.children[1].value))
        if ast.value == "[]":
            lhs = interpret(ast.children[0], env)
            if isinstance(lhs, Error): return lhs
            rhs = interpret(ast.children[1], env)
            if isinstance(rhs, Error): return rhs
            return lhs.get(rhs)
    elif ast.typ == "PREOP":
        if ast.value == "+":
            return interpret(ast.children[0], env)
        elif ast.value == "-":
            return interpret(ast.children[0], env).negative()
        elif ast.value == "!":
            return not interpret(ast.children[0], env)
        elif ast.value == "%":
            return Number(value = len(interpret(ast.children[0], env)))