from teeny.AST import AST
from teeny.value import Value, Number, String, Table, Closure, Nil, Env, Error, ValError, BuiltinClosure, Underscore\
    , snapshot, isTruthy, match, makeObject, makeTable
from teeny.glob import makeGlobal
from teeny.exception import RuntimeError

def assignVariable(lhs: AST, rhs: Value, env: Env, isDeclare: bool = False, defAssign: bool = False):
    if lhs.typ != "TABLE":
        if lhs.typ == "NAME":
            if lhs.value == "_":
                return Nil()
            if isDeclare:
                env.define(lhs.value, rhs)
                return rhs
            else:
                if not defAssign or (isinstance(env.read(lhs.value), Nil) or env.read(lhs.value) == None):
                    val = env.write(lhs.value, rhs)
                    if isinstance(val, Error): return val
                    return rhs
                return env.read(lhs.value)
        elif lhs.value == ".":
            l = interpret(lhs.children[0], env)
            r = String(value = lhs.children[1].value)
            if isDeclare:
                l.define(r, rhs)
                return rhs
            else:
                if not defAssign or (isinstance(l.get(r), Nil) or l.get(r) == None):
                    val = l.set(r, rhs)
                    if isinstance(val, Error): return val
                    return rhs
                return l.get(r)
        elif lhs.value == "[]":
            l = interpret(lhs.children[0], env)
            r = interpret(lhs.children[1], env)
            if isDeclare:
                l.define(r, rhs)
                return rhs
            else:
                if not defAssign or (isinstance(l.get(r), Nil) or l.get(r) == None):
                    val = l.set(r, rhs)
                    if isinstance(val, Error): return val
                    return rhs
                return l.get(r)
    else:
        cnt: int = 0
        res = Table({})
        for c in lhs.children:
            if c.typ == "PAIR":
                val = assignVariable(c.children[1], rhs.get(String(value = c.children[0].value)), env, isDeclare, defAssign)
                if isinstance(val, Error): return val
                res.define(String(value = c.children[0].value), val)
            elif c.typ == "NAME" and not isinstance(rhs.get(String(value = c.value)), Nil):
                val = assignVariable(c, rhs.get(String(value = c.value)), env, isDeclare, defAssign)
                if isinstance(val, Error): return val
                res.append(val)
            else:
                val = assignVariable(c, rhs.get(Number(value = cnt)), env, isDeclare, defAssign)
                if isinstance(val, Error): return val
                cnt += 1
                res.append(val)
        return res

def interpret(ast: AST, env: Env = makeGlobal(), **kwargs) -> Value:
    if ast.typ == "NUMBER":
        return Number(value = float(ast.value))
    if ast.typ == "STRING":
        if ast.value != None:
            return String(value = (str(ast.value)[1:-1]))
        else:
            res = String(value = "")
            for c in ast.children:
                val = interpret(c, env)
                res = res + val
            return res
    elif ast.typ == "NAME":
        if ast.value == "nil":
            return Nil()
        if ast.value == "_":
            return Underscore()
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
                    value.update({key: val})
            else:
                val = interpret(c, env)
                if isinstance(val, Error): return val
                value.append(val)
        return value
    elif ast.typ == "FN":
        res = []
        for v in ast.value:
            if isinstance(v, list):
                val = interpret(v[1], env)
                if isinstance(val, Error): return val
                res.append([v[0], val])
            else:
                res.append(v)
        value = Closure(res, ast.children, Env(outer = env), False)
        return value
    elif ast.typ == "FN-DYNAMIC":
        res = []
        for v in ast.value:
            if isinstance(v, list):
                val = interpret(v[1], env)
                if isinstance(val, Error): return val
                res.append([v[0], val])
            else:
                res.append(v[0])
        value = Closure(res, ast.children, Env(outer = env), True)
        return value
    elif ast.typ == "CALL":
        value = interpret(ast.children[0], env)
        if isinstance(value, Error): return value
        piped = None
        pipedUsed = False
        if kwargs.get("piped") != None:
            piped = kwargs.get("piped")
        params = ast.children[1:]
        kwArg = {}
        par = []
        for pos, p in enumerate(params):
            if p.typ == "NAME" and p.value == "_":
                par.append(piped)
                pipedUsed = True
                continue
            if p.typ != "KWARG":
                val = interpret(p, env)
                if isinstance(val, Error): return val
                par.append(val)
            else:
                lhs = p.children[0]; rhs = p.children[1]
                val = interpret(rhs, env)
                kwArg[lhs.value] = val
        if not pipedUsed and piped != None:
            par.insert(0, piped)
        if isinstance(value, BuiltinClosure):
            if value.hasEnv:
                return value([*par, env], kwArg)
        return value(par, kwArg)
    elif ast.typ == "IF":
        value = interpret(ast.children[0], env)
        if isinstance(value, Error): return value
        if isTruthy(value):
            return interpret(ast.children[1], env)
        for c in ast.children[2:]:
            if c.typ == "ELIF":
                value = interpret(c.children[0], env)
                if isinstance(value, Error): return value
                if isTruthy(value):
                    return interpret(c.children[1], env)
        if ast.children[-1].typ == "ELSE":
            return interpret(ast.children[-1].children[0], env)
        return Nil()
    elif ast.typ == "WHILE":
        res = Nil()
        val = interpret(ast.children[0], env)
        if isinstance(val, Error): return val
        while isTruthy(val):
            res = interpret(ast.children[1], env)
            if isinstance(res, Error): return res
            val = interpret(ast.children[0], env)
            if isinstance(val, Error): return val
        return res
    elif ast.typ == "FOR":
        lhs = ast.children[0]
        rhs = interpret(ast.children[1], env)
        if isinstance(rhs, Error): return rhs
        if not isinstance(rhs, Table):
            return Error(typ = "Runtime Error", value = "iterate non-Table")
        curEnv = snapshot(env)
        lst = Table()
        st = rhs.get(String(value = "_iter_"))([], {})
        v = st([], {})
        while not isinstance(v, Nil):
            p = v
            env = snapshot(curEnv)
            assignVariable(lhs, rhs.get(Number(value = p)), env, True)
            val = interpret(ast.children[2], env)
            if isinstance(val, Error): return val
            lst.append(val)
            v = st([], {})
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
        nEnv = Env(env)
        val = interpret(ast.value, env)
        if isinstance(val, Error): return val
        for c in ast.children:
            lft = interpret(c.children[0], nEnv)
            if isinstance(lft, Error): return lft
            if not isinstance(lft, Closure) and not isinstance(lft, BuiltinClosure):
                if match(lft, val):
                    return interpret(c.children[1], nEnv)
            else:
                if isTruthy(lft([val], {})):
                    return interpret(c.children[1], nEnv)
        return Nil()
    elif ast.typ == "TRY":
        val = interpret(ast.children[0], env)
        if isinstance(val, Error):
            rhs = interpret(ast.children[1], env)
            if not isinstance(rhs, (Closure, BuiltinClosure, Table)):
                return Error(typ = 'Runtime Error', value = 'uncallable catch expression')
            return rhs([ValError(typ = val.typ, value = val.value)], {})
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
            lhs = interpret(ast.children[0], env)
            if not isTruthy(lhs):
                return Number(value = 0)
            elif not isTruthy(interpret(ast.children[1], env)):
                return Number(value = 0)
            else:
                return Number(value = 1)
        if ast.value == "||":
            lhs = interpret(ast.children[0], env)
            if isTruthy(lhs):
                return Number(value = 1)
            elif isTruthy(interpret(ast.children[1], env)):
                return Number(value = 1)
            else:
                return Number(value = 0)
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
        if ast.value == "??":
            lhs = interpret(ast.children[0], env)
            if isinstance(lhs, Error): return lhs
            if not isinstance(lhs, Nil): return lhs
            rhs = interpret(ast.children[1], env)
            return rhs
        if ast.value == "..":
            lhs = interpret(ast.children[0], env)
            if isinstance(lhs, Error): return lhs
            if not isinstance(lhs, Number): return Error(typ = 'Runtime Error', value = 'non-Number in range operator')
            rhs = interpret(ast.children[1], env)
            if isinstance(rhs, Error): return rhs
            if not isinstance(rhs, Number): return Error(typ = 'Runtime Error', value = 'non-Number in range operator')
            return makeTable(list(range(int(lhs.value), int(rhs.value) + 1)))
        if ast.value == ":=":
            # The left is guarenteed a name or a Table
            val = interpret(ast.children[1], env)
            if isinstance(val, Error): return val
            return assignVariable(ast.children[0], val, env, True)
        if ast.value == "=":
            # The left is guarenteed a name or a Table
            val = interpret(ast.children[1], env)
            if isinstance(val, Error): return val
            return assignVariable(ast.children[0], val, env, False)
        if ast.value == "?=":
            # The left is guarenteed a name or a Table
            val = interpret(ast.children[1], env)
            if isinstance(val, Error): return val
            return assignVariable(ast.children[0], val, env, False, True)
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
        if ast.value == "|>":
            lhs = interpret(ast.children[0], env)
            if isinstance(lhs, Error): return lhs
            rhs = interpret(ast.children[1], env, piped = lhs)
            return rhs
    elif ast.typ == "PREOP":
        if ast.value == "+":
            return interpret(ast.children[0], env)
        elif ast.value == "-":
            return interpret(ast.children[0], env).negative()
        elif ast.value == "!":
            return Number(value = not isTruthy(interpret(ast.children[0], env)))
    elif ast.typ == "SUFOP":
        if ast.value == "!":
            return interpret(ast.children[0], env).fact()