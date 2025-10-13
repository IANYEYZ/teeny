from teeny.value import Env, Number, String, Table, BuiltinClosure
import math
from pathlib import Path

Math = Table({
    String("pi"): Number(math.pi), String("e"): Number(math.e)
})

srcPath = Path(__file__).parent.parent.parent / "example"

def Import(name: String) -> Table:
    code = open(srcPath / name.value).read()
    from teeny.runner import run
    res = run(code)
    # res.get("export")
    # print(res)
    return res.get("export")

def Mix(table: Table, env: Env):
    for key in table.value.keys():
        if isinstance(key, String):
            env.define(key.value, table.get(key))

def makeGlobal() -> Env:
    gEnv = Env()
    gEnv.update({
        "math": Math,
        "print": BuiltinClosure(lambda *x: print(*x, sep = '', end = '')),
        "input": BuiltinClosure(lambda: input("")),
        "export": Table({}),
        "import": BuiltinClosure(Import),
        "mix": BuiltinClosure(Mix, True),
        "include": BuiltinClosure(lambda name, env: Mix(Import(name), env), True)
    })
    return gEnv