from teeny.AST import AST
from teeny.value import Value, Number, String, Table, Closure, Nil, Env, BuiltinClosure, snapshot, isTruthy
from teeny.glob import makeGlobal
from teeny.exception import RuntimeError

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
            blocks = ast.children[1:]
            lst = Nil()
            for b in blocks:
                if b.typ == "ELSE": break
                lst = interpret(b, env)
            return lst
        else:
            if ast.children[-1].typ == "ELSE":
                blocks = ast.children[-1].children
                lst = Nil()
                for b in blocks:
                    lst = interpret(b, env)
                return lst
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
            print(p)
            env = snapshot(curEnv)
            if lhs.typ == "NAME":
                name = lhs.value
                val = rhs.get(Number(value = p))
                env.define(name, val)
            else:
                children = lhs.children
                val = rhs.get(Number(value = p))
                if not isinstance(val, Table):
                    raise RuntimeError("Expect Table at the right side of table-binding")
                cnt = 0
                for c in children:
                    if val.get(String(value = c.value)) != None:
                        env.define(c.value, val.get(String(value = c.value)))
                    else:
                        if val.size <= cnt:
                            raise RuntimeError("Too few items inside the right side of table-binding")
                        env.define(c.value, val.get(Number(value = cnt)))
                        cnt += 1
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
            val = None
            lhs = None
            if ast.children[0].typ == 'NAME':
                lhs = ast.children[0].value
                val = interpret(ast.children[1], env)
                env.define(lhs, val)
            else:
                lhs = ast.children[0].children
                val = interpret(ast.children[1], env)
                if not isinstance(val, Table):
                    raise RuntimeError("Expect Table at the right side of table-binding")
                cnt = 0
                for c in lhs:
                    if val.get(String(value = c.value)) != None:
                        env.define(c.value, val.get(String(value = c.value)))
                    else:
                        if val.size <= cnt:
                            raise RuntimeError("Too few items inside the right side of table-binding")
                        env.define(c.value, val.get(Number(value = cnt)))
                        cnt += 1
            return val
        if ast.value == "=":
            # The left is guarenteed a name or a Table
            val = None
            if ast.children[0].typ == 'NAME':
                lhs = ast.children[0].value
                val = interpret(ast.children[1], env)
                env.write(lhs, val)
            else:
                lhs = ast.children[0].children
                val = interpret(ast.children[1], env)
                if not isinstance(val, Table):
                    raise RuntimeError("Expect Table at the right side of table-binding")
                cnt = 0
                for c in lhs:
                    if val.get(String(value = c.value)) != None:
                        env.write(c.value, val.get(String(value = c.value)))
                    else:
                        if val.size <= cnt:
                            raise RuntimeError("Too few items inside the right side of table-binding")
                        env.write(c.value, val.get(Number(value = cnt)))
                        cnt += 1
            return val
        if ast.value == ".":
            lhs = interpret(ast.children[0], env)
            return lhs.get(String(value = ast.children[1].value))
        if ast.value == "[]":
            lhs = interpret(ast.children[0], env)
            rhs = interpret(ast.children[1], env)
            return lhs.get(rhs)
        if ast.value == "[]=":
            lhs = interpret(ast.children[0], env)
            rhs = interpret(ast.children[1], env)
            val = interpret(ast.children[2], env)
            lhs.set(rhs, val)
            return val
        if ast.value == "[]:=":
            lhs = interpret(ast.children[0], env)
            rhs = interpret(ast.children[1], env)
            val = interpret(ast.children[2], env)
            lhs.define(rhs, val)
            return val
        if ast.value == ".=":
            lhs = interpret(ast.children[0], env)
            rhs = String(value = ast.children[1].value)
            val = interpret(ast.children[2], env)
            lhs.set(rhs, val)
        if ast.value == ".:=":
            lhs = interpret(ast.children[0], env)
            rhs = String(value = ast.children[1].value)
            val = interpret(ast.children[2], env)
            lhs.define(rhs, val)
            return val
    elif ast.typ == "PREOP":
        if ast.value == "+":
            return interpret(ast.children[0], env)
        elif ast.value == "-":
            return interpret(ast.children[0], env).negative()
        elif ast.value == "!":
            return not interpret(ast.children[0], env)
        elif ast.value == "%":
            return Number(value = len(interpret(ast.children[0], env)))