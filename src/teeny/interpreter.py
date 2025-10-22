from teeny.AST import AST
from teeny.value import Value, Number, String, Table, Closure, Nil, Env, BuiltinClosure, snapshot, isTruthy
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
                    value.update({String(value = c.children[0].value): interpret(c.children[1], env)})
                else:
                    value.update({interpret(c.children[0], env): interpret(c.children[1], env)})
            else:
                value.append(interpret(c, env))
        return value
    elif ast.typ == "FN":
        value = Closure(ast.value, ast.children, Env(outer = env), False)
        return value
    elif ast.typ == "FN-DYNAMIC":
        value = Closure(ast.value, ast.children, Env(outer = env), True)
        return value
    elif ast.typ == "CALL":
        value = interpret(ast.children[0], env)
        params = ast.children[1:]
        for pos, p in enumerate(params):
            params[pos] = interpret(p, env)
        if isinstance(value, BuiltinClosure):
            if value.hasEnv:
                return value([*params, env])
        return value(params)
    elif ast.typ == "IF":
        value = interpret(ast.children[0], env)
        if isTruthy(value):
            return interpret(ast.children[1])
        for c in ast.children[2:]:
            if c.typ == "ELIF":
                value = interpret(c.children[0], env)
                if isTruthy(value):
                    return interpret(c.children[1], env)
        if ast.children[-1].typ == "ELSE":
            return interpret(ast.children[-1].children[0])
        return Nil()
    elif ast.typ == "WHILE":
        res = Nil()
        while isTruthy(interpret(ast.children[0], env)):
            res = interpret(ast.children[1])
        return res
    elif ast.typ == "FOR":
        lhs = ast.children[0]
        rhs = interpret(ast.children[1])
        if not isinstance(rhs, Table):
            raise RuntimeError("Only Table is iterrable")
        curEnv = snapshot(env)
        lst = Table()
        st = rhs.get(String(value = "_iter_"))([])
        v = st()
        while not isinstance(v, Nil):
            p = v
            env = snapshot(curEnv)
            assignVariable(lhs, rhs.get(Number(value=p)), env, True)
            lst.append(interpret(ast.children[2], env))
            v = st()
        env = snapshot(curEnv)
        return lst
    elif ast.typ == "BLOCK":
        lst = Nil()
        nEnv = Env(env)
        for b in ast.children:
            lst = interpret(b, nEnv)
        return lst
    elif ast.typ == "MATCH":
        val = interpret(ast.value, env)
        nEnv = Env(env)
        for c in ast.children:
            if c.typ != "OPT":
                raise RuntimeError("OPT is the only type allowed inside a match expression")
            lft = interpret(c.children[0], nEnv) if c.children[0].value != '_' else Number(1)
            if isTruthy(lft == val):
                return interpret(c.children[1], nEnv)
        return Nil()
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
            assignVariable(ast.children[0], val, env, True)
            return val
        if ast.value == "=":
            # The left is guarenteed a name or a Table
            val = interpret(ast.children[1], env)
            assignVariable(ast.children[0], val, env, False)
            return val
        if ast.value == ".":
            lhs = interpret(ast.children[0], env)
            return lhs.get(String(value = ast.children[1].value))
        if ast.value == "[]":
            lhs = interpret(ast.children[0], env)
            rhs = interpret(ast.children[1], env)
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