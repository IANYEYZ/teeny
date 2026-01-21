from teeny.AST import AST
from teeny.value import Bubble, Value, Number, String, Table, Closure, Nil, Env, Error, ValError, BuiltinClosure, Underscore\
    , snapshot, isTruthy, match, makeObject, makeTable, Regex
from teeny.glob import makeGlobal
from typing import Callable

def assignVariable(lhs: AST, rhs: Value, env: Env, isDeclare: bool = False, 
                   assignConfig: Callable = lambda a, b: b) -> Value:
    if lhs.typ != "TABLE":
        if lhs.typ == "NAME":
            return env.define(lhs.value, rhs)
        elif lhs.value == ".":
            l = interpret(lhs.children[0], env)
            r = String(value = lhs.children[1].value)
            val = l.set(r, assignConfig(l.get(r), rhs))
            if isinstance(val, Error): return val
            return l.take(r)
        elif lhs.value == "[]":
            l = interpret(lhs.children[0], env)
            r = interpret(lhs.children[1], env)
            val = l.set(r, assignConfig(l.get(r), rhs))
            if isinstance(val, Error): return val
            return l.take(r)
    else:
        cnt: int = 0
        res = Table({})
        for c in lhs.children:
            if c.typ == "PAIR":
                val = assignVariable(c.children[1], rhs.get(String(value = c.children[0].value)), env, isDeclare, assignConfig)
                if isinstance(val, Error): return val
                res.define(String(value = c.children[0].value), val)
            elif c.typ == "NAME" and not isinstance(rhs.get(String(value = c.value)), Nil):
                val = assignVariable(c, rhs.get(String(value = c.value)), env, isDeclare, assignConfig)
                if isinstance(val, Error): return val
                res.append(val)
            else:
                val = assignVariable(c, rhs.get(Number(value = cnt)), env, isDeclare, assignConfig)
                if isinstance(val, Error): return val
                cnt += 1
                res.append(val)
        return res

def interpret(ast: AST, env: Env = makeGlobal(), **kwargs) -> Value:
    if ast.typ == "NUMBER":
        return Number(value = float(ast.value))
    elif ast.typ == "STRING":
        if ast.value != None:
            return String(value = (str(ast.value).replace("\\{", "{").replace("\\}", "}")))
        else:
            res = String(value = "")
            for c in ast.children:
                val = interpret(c, env)
                res = res + val.toString()
            return res
    elif ast.typ == "REGEX":
        return Regex(value = ast.value)
    elif ast.typ == "NAME":
        if ast.value == "nil":
            return Nil()
        if ast.value == "_":
            return Underscore()
        val = env.read(ast.value)
        if kwargs.get("piped") != None:
            return val([kwargs.get("piped")], [])
        return val
    elif ast.typ == "RETURN":
        val = interpret(ast.children[0], env)
        if isinstance(val, Error) or isinstance(val, Bubble): return val
        return Bubble(typ = "RETURN", val = val)
    elif ast.typ == "BREAK":
        if len(ast.children) == 0:
            return Bubble(typ = "BREAK", val = Nil())
        val = interpret(ast.children[0], env)
        if isinstance(val, Error) or isinstance(val, Bubble): return val
        return Bubble(typ = "BREAK", val = val)
    elif ast.typ == "CONTINUE":
        if len(ast.children) == 0:
            return Bubble(typ = "CONTINUE", val = Nil())
        val = interpret(ast.children[0], env)
        if isinstance(val, Error) or isinstance(val, Bubble): return val
        return Bubble(typ = "CONTINUE", val = val)
    elif ast.typ == "TABLE":
        value = Table({})
        for c in ast.children:
            if c.typ == "PAIR":
                # c.children[0] is guareenteed a NAME or a VALUE
                if c.children[0].typ == "NAME":
                    if len(c.children) == 1:
                        val = interpret(c.children[0], env)
                        if isinstance(val, Error) or isinstance(val, Bubble): return val
                        value.update({String(value = c.children[0].value): val})
                    else:
                        val = interpret(c.children[1], env)
                        if isinstance(val, Error) or isinstance(val, Bubble): return val
                        value.update({String(value = c.children[0].value): val})
                else:
                    key = interpret(c.children[0], env)
                    if isinstance(key, Error) or isinstance(key, Bubble): return key
                    val = interpret(c.children[1], env)
                    if isinstance(val, Error) or isinstance(val, Bubble): return val
                    value.update({key: val})
            elif c.value == "...":
                val = interpret(c.children[0], env)
                if isinstance(val, Error): return val
                if not isinstance(val, Table):
                    return Error(typ = "Runtime Error", value = "spread operator on non-Table")
                for k in val.value.keys():
                    v = val.get(k)
                    if isinstance(v, Error) or isinstance(v, Bubble): return v
                    if isinstance(k, Number):
                        value.append(v)
                    else:
                        value.update({k: v})
            else:
                val = interpret(c, env)
                if isinstance(val, Error) or isinstance(val, Bubble): return val
                value.append(val)
        return value
    elif ast.typ == "FN":
        res = []
        for v in ast.value:
            if isinstance(v, list):
                if len(v) == 1:
                    res.append([v[0]])
                else:
                    val = interpret(v[1], env)
                    if isinstance(val, Error) or isinstance(val, Bubble): return val
                    res.append([v[0], val])
            else:
                res.append(v)
        value = Closure(res, ast.children, Env(outer = env), False)
        if kwargs.get("piped") != None:
            return value([kwargs.get("piped")], [])
        return value
    elif ast.typ == "FN-DYNAMIC":
        res = []
        for v in ast.value:
            if isinstance(v, list):
                val = interpret(v[1], env)
                if isinstance(val, Error) or isinstance(val, Bubble): return val
                res.append([v[0], val])
            else:
                res.append(v)
        value = Closure(res, ast.children, Env(outer = env), True)
        if kwargs.get("piped") != None:
            return value([kwargs.get("piped")], [])
        return value
    elif ast.typ == "CALL":
        value = interpret(ast.children[0], env)
        if isinstance(value, Error) or isinstance(value, Bubble): return value
        piped = None
        pipedUsed = False
        if kwargs.get("piped") != None:
            piped = kwargs.get("piped")
        params = ast.children[1:]
        kwArg = []
        par = []
        for pos, p in enumerate(params):
            if p.typ == "NAME" and p.value == "_":
                par.append(piped)
                pipedUsed = True
                continue
            if p.value == "...":
                val = interpret(p.children[0], env)
                if isinstance(val, Error) or isinstance(val, Bubble): return val
                if not isinstance(val, Table):
                    return Error(typ = "Runtime Error", value = "spread operator on non-Table")
                for k in val.value.keys():
                    v = val.get(k)
                    if isinstance(v, Error) or isinstance(v, Bubble): return v
                    if isinstance(k, Number):
                        par.append(v)
                    else:
                        kwArg.append([k, v])
            elif p.typ != "KWARG":
                val = interpret(p, env)
                if isinstance(val, Error) or isinstance(val, Bubble): return val
                par.append(val)
            else:
                lhs = p.children[0]; rhs = p.children[1]
                val = interpret(rhs, env)
                if isinstance(val, Error) or isinstance(val, Bubble): return val
                kwArg.append([lhs, val])
        if not pipedUsed and piped != None:
            par.insert(0, piped)
        if isinstance(value, BuiltinClosure):
            if value.hasEnv:
                return value([*par, env], kwArg)
        return value(par, kwArg)
    elif ast.typ == "IF":
        value = interpret(ast.children[0], env)
        if isinstance(value, Error) or isinstance(value, Bubble): return value
        if isTruthy(value):
            return interpret(ast.children[1], env)
        for c in ast.children[2:]:
            if c.typ == "ELIF":
                value = interpret(c.children[0], env)
                if isinstance(value, Error) or isinstance(value, Bubble): return value
                if isTruthy(value):
                    return interpret(c.children[1], env)
        if ast.children[-1].typ == "ELSE":
            return interpret(ast.children[-1].children[0], env)
        return Nil()
    elif ast.typ == "WHILE":
        res = Nil()
        val = interpret(ast.children[0], env)
        if isinstance(val, Error) or isinstance(val, Bubble): return val
        while isTruthy(val):
            res = interpret(ast.children[1], env)
            if isinstance(res, Error) or isinstance(res, Bubble): return res if isinstance(res, Error) else res.val
            val = interpret(ast.children[0], env)
            if isinstance(val, Error) or isinstance(val, Bubble): return val if isinstance(val, Error) else val.val
        return res
    elif ast.typ == "FOR":
        lhs = ast.children[0]
        rhs = interpret(ast.children[1], env)
        if isinstance(rhs, Error) or isinstance(rhs, Bubble): return rhs
        if rhs.get(String(value = "_iter_")) == Nil():
            return Error(typ = "Runtime Error", value = "iterate non-Iterable")
        curEnv = snapshot(env)
        lst = Table()
        st = rhs.get(String(value = "_iter_"))([], [])
        v = st()
        while not isinstance(v, Nil):
            p = v
            env = snapshot(curEnv)
            assignVariable(lhs, rhs.take(p), env, True)
            val = interpret(ast.children[2], env)
            if isinstance(val, Bubble):
                if val.typ == "BREAK":
                    lst.append(val.val)
                    break
                elif val.typ == "CONTINUE":
                    lst.append(val.val)
                    v = st()
                    continue
                else: return val
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
            if isinstance(lst, Bubble): return lst
            if isinstance(lst, Error): return lst
        return lst
    elif ast.typ == "MATCH":
        nEnv = Env(env)
        val = None
        if not isinstance(ast.value, list):
            val = interpret(ast.value, env)
        else:
            val = interpret(ast.value[0], env)
            assignVariable(ast.value[1], val, nEnv, True, False)
        if isinstance(val, Error) or isinstance(val, Bubble): return val
        for c in ast.children:
            if match(c.children[0], val, nEnv):
                return interpret(c.children[1], nEnv)
        return Nil()
    elif ast.typ == "TRY":
        val = interpret(ast.children[0], env)
        if isinstance(val, Bubble):
            return val
        if isinstance(val, Error):
            rhs = interpret(ast.children[1], env)
            if not isinstance(rhs, (Closure, BuiltinClosure, Table)):
                return Error(typ = 'Runtime Error', value = 'uncallable catch expression')
            return rhs([ValError(typ = val.typ, value = val.value)], [])
        else:
            return val
    elif ast.typ == "OP":
        if ast.value == "+":
            lhs = interpret(ast.children[0], env)
            if isinstance(lhs, Error) or isinstance(lhs, Bubble): return lhs
            rhs = interpret(ast.children[1], env)
            if isinstance(rhs, Error) or isinstance(rhs, Bubble): return rhs
            return lhs + rhs
        if ast.value == "-":
            lhs = interpret(ast.children[0], env)
            if isinstance(lhs, Error) or isinstance(lhs, Bubble): return lhs
            rhs = interpret(ast.children[1], env)
            if isinstance(rhs, Error) or isinstance(rhs, Bubble): return rhs
            return lhs - rhs
        if ast.value == "*":
            lhs = interpret(ast.children[0], env)
            if isinstance(lhs, Error) or isinstance(lhs, Bubble): return lhs
            rhs = interpret(ast.children[1], env)
            if isinstance(rhs, Error) or isinstance(rhs, Bubble): return rhs
            return lhs * rhs
        if ast.value == "/":
            lhs = interpret(ast.children[0], env)
            if isinstance(lhs, Error) or isinstance(lhs, Bubble): return lhs
            rhs = interpret(ast.children[1], env)
            if isinstance(rhs, Error) or isinstance(rhs, Bubble): return rhs
            return lhs / rhs
        if ast.value == "%":
            lhs = interpret(ast.children[0], env)
            if isinstance(lhs, Error) or isinstance(lhs, Bubble): return lhs
            rhs = interpret(ast.children[1], env)
            if isinstance(rhs, Error) or isinstance(rhs, Bubble): return rhs
            return lhs % rhs
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
            lhs = interpret(ast.children[0], env)
            if isinstance(lhs, Error) or isinstance(lhs, Bubble): return lhs
            rhs = interpret(ast.children[1], env)
            if isinstance(rhs, Error) or isinstance(rhs, Bubble): return rhs
            return lhs == rhs
        if ast.value == "!=":
            lhs = interpret(ast.children[0], env)
            if isinstance(lhs, Error) or isinstance(lhs, Bubble): return lhs
            rhs = interpret(ast.children[1], env)
            if isinstance(rhs, Error) or isinstance(rhs, Bubble): return rhs
            return lhs != rhs
        if ast.value == ">":
            lhs = interpret(ast.children[0], env)
            if isinstance(lhs, Error) or isinstance(lhs, Bubble): return lhs
            rhs = interpret(ast.children[1], env)
            if isinstance(rhs, Error) or isinstance(rhs, Bubble): return rhs
            return lhs > rhs
        if ast.value == "<":
            lhs = interpret(ast.children[0], env)
            if isinstance(lhs, Error) or isinstance(lhs, Bubble): return lhs
            rhs = interpret(ast.children[1], env)
            if isinstance(rhs, Error) or isinstance(rhs, Bubble): return rhs
            return lhs < rhs
        if ast.value == ">=":
            lhs = interpret(ast.children[0], env)
            if isinstance(lhs, Error) or isinstance(lhs, Bubble): return lhs
            rhs = interpret(ast.children[1], env)
            if isinstance(rhs, Error) or isinstance(rhs, Bubble): return rhs
            return lhs >= rhs
        if ast.value == "<=":
            lhs = interpret(ast.children[0], env)
            if isinstance(lhs, Error) or isinstance(lhs, Bubble): return lhs
            rhs = interpret(ast.children[1], env)
            if isinstance(rhs, Error) or isinstance(rhs, Bubble): return rhs
            return lhs <= rhs
        if ast.value == "=~":
            lhs = interpret(ast.children[0], env)
            if not isinstance(lhs, String): return Error("Runtime Error", "match equal on non-String")
            rhs = interpret(ast.children[1], env)
            if not isinstance(rhs, Regex): return Error("Runtime Error", "match equal on non-Regex")
            return rhs.match(lhs)
        if ast.value == "??":
            lhs = interpret(ast.children[0], env)
            if isinstance(lhs, Error) or isinstance(lhs, Bubble): return lhs
            if not isinstance(lhs, Nil): return lhs
            rhs = interpret(ast.children[1], env)
            return rhs
        if ast.value == "?:":
            lhs = interpret(ast.children[0], env)
            if isinstance(lhs, Error) or isinstance(lhs, Bubble): return lhs
            if isTruthy(lhs): return lhs
            rhs = interpret(ast.children[1], env)
            return rhs
        if ast.value == "..":
            lhs = interpret(ast.children[0], env)
            if isinstance(lhs, Error) or isinstance(lhs, Bubble): return lhs
            if not isinstance(lhs, Number): return Error(typ = 'Runtime Error', value = 'non-Number in range operator')
            rhs = interpret(ast.children[1], env)
            if isinstance(rhs, Error) or isinstance(rhs, Bubble): return rhs
            if not isinstance(rhs, Number): return Error(typ = 'Runtime Error', value = 'non-Number in range operator')
            return makeTable(list(range(int(lhs.value), int(rhs.value) + 1)))
        if ast.value == ":=":
            # The left is guarenteed a name or a Table
            val = interpret(ast.children[1], env)
            if isinstance(val, Error) or isinstance(val, Bubble): return val
            return assignVariable(ast.children[0], val, env, True)
        if ast.value == "=":
            # The left is guarenteed a name or a Table
            val = interpret(ast.children[1], env)
            if isinstance(val, Error) or isinstance(val, Bubble): return val
            return assignVariable(ast.children[0], val, env, False)
        if ast.value == "?=":
            # The left is guarenteed a name or a Table
            val = interpret(ast.children[1], env)
            if isinstance(val, Error) or isinstance(val, Bubble): return val
            return assignVariable(ast.children[0], val, env, False,
                                  lambda a, b: b if a == Nil() else a)
        if ast.value == "+=":
            # The left is guarenteed a name or a Table
            val = interpret(ast.children[1], env)
            if isinstance(val, Error) or isinstance(val, Bubble): return val
            return assignVariable(ast.children[0], val, env, False,
                                  lambda a, b: a + b)
        if ast.value == "-=":
            # The left is guarenteed a name or a Table
            val = interpret(ast.children[1], env)
            if isinstance(val, Error) or isinstance(val, Bubble): return val
            return assignVariable(ast.children[0], val, env, False,
                                  lambda a, b: a - b)
        if ast.value == "*=":
            # The left is guarenteed a name or a Table
            val = interpret(ast.children[1], env)
            if isinstance(val, Error) or isinstance(val, Bubble): return val
            return assignVariable(ast.children[0], val, env, False,
                                  lambda a, b: a * b)
        if ast.value == "/=":
            # The left is guarenteed a name or a Table
            val = interpret(ast.children[1], env)
            if isinstance(val, Error) or isinstance(val, Bubble): return val
            return assignVariable(ast.children[0], val, env, False,
                                  lambda a, b: a / b)
        if ast.value == "%=":
            # The left is guarenteed a name or a Table
            val = interpret(ast.children[1], env)
            if isinstance(val, Error) or isinstance(val, Bubble): return val
            return assignVariable(ast.children[0], val, env, False,
                                  lambda a, b: a % b)
        if ast.value == ".":
            lhs = interpret(ast.children[0], env)
            if isinstance(lhs, Error) or isinstance(lhs, Bubble): return lhs
            return lhs.take(String(value = ast.children[1].value))
        if ast.value == "[]":
            lhs = interpret(ast.children[0], env)
            if isinstance(lhs, Error) or isinstance(lhs, Bubble): return lhs
            rhs = interpret(ast.children[1], env)
            if isinstance(rhs, Error) or isinstance(rhs, Bubble): return rhs
            return lhs.take(rhs)
        if ast.value == "|>":
            lhs = interpret(ast.children[0], env)
            if isinstance(lhs, Error) or isinstance(lhs, Bubble): return lhs
            if ast.children[1].typ == "CALL": rhs = interpret(ast.children[1], env, piped = lhs)
            else:
                rhs = interpret(ast.children[1], env)
                if isinstance(rhs, Error) or isinstance(rhs, Bubble): return rhs
                return rhs([lhs], [])
            return rhs
        if ast.value.startswith("<") and ast.value.endswith(">"):
            lhs = interpret(ast.children[0], env)
            if isinstance(lhs, Error) or isinstance(lhs, Bubble): return lhs
            rhs = interpret(ast.children[1], env)
            if isinstance(rhs, Error) or isinstance(rhs, Bubble): return rhs
            # For custom infix operators, we define them as functions in the environment
            funcName = f"infix_{ast.value[1:-1]}"
            func = env.read(funcName)
            if isinstance(func, Error) or isinstance(func, Bubble):
                return func
            elif not callable(func):
                return Error(typ = "Runtime Error", value = f"infix operator {ast.value} is not callable")
            return func([lhs, rhs], [])
    elif ast.typ == "PREOP":
        if ast.value == "+":
            return interpret(ast.children[0], env)
        elif ast.value == "-":
            lhs = interpret(ast.children[0], env)
            if isinstance(lhs, Error) or isinstance(lhs, Bubble): return lhs
            return lhs.negative()
        elif ast.value == "!":
            lhs = interpret(ast.children[0], env)
            if isinstance(lhs, Error) or isinstance(lhs, Bubble): return lhs
            return Number(value = not isTruthy(lhs))
    elif ast.typ == "SUFOP":
        if ast.value == "!":
            lhs = interpret(ast.children[0], env)
            if isinstance(lhs, Error) or isinstance(lhs, Bubble): return lhs
            return lhs.fact()
        elif ast.value == "?":
            lhs = interpret(ast.children[0], env)
            if isinstance(lhs, Error) or isinstance(lhs, Bubble): return lhs
            return Number(value = isTruthy(lhs))
