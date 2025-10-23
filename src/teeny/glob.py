from teeny.value import Env, Number, String, Table, Error, ValError, BuiltinClosure
import math
from pathlib import Path

Math = Table({
    String(value = "pi"): Number(value = math.pi), String(value = "e"): Number(value = math.e)
})

srcPath = Path(__file__).parent.parent.parent / "example"

def Import(name: String) -> Table:
    code = open(srcPath / name.value).read()
    from teeny.runner import run
    res = run(code)
    return res.get("export")

def Mix(table: Table, env: Env):
    for key in table.value.keys():
        if isinstance(key, String):
            env.define(key.value, table.get(key))

def makeGlobal() -> Env:
    gEnv = Env()
    gEnv.update({
        "math": Math,
        "print": BuiltinClosure(fn = lambda *x: print(*x, sep = '', end = '')),
        "input": BuiltinClosure(fn = lambda: input("")),
        "export": Table(value = {}),
        "import": BuiltinClosure(fn = Import),
        "mix": BuiltinClosure(fn = Mix, hasEnv = True),
        "include": BuiltinClosure(fn = lambda name, env: Mix(Import(name), env), hasEnv = True),
        "error": BuiltinClosure(fn = lambda typ, message: ValError(typ = typ, value = message)),
        "panic": BuiltinClosure(fn = lambda err: Error({}, err.typ, err.value))
    })
    return gEnv