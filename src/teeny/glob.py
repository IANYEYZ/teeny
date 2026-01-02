import importlib
from teeny.value import Env, Number, String, Table, Error, ValError, BuiltinClosure, \
                        makeTable, makeObject, Value, Nil, Closure, copy, isTruthy
import math
from pathlib import Path
import json
import os
import shutil
import requests
import sys
import random
import subprocess
import time
import functools
import statistics
from collections.abc import Callable
import sqlite3

srcPath: Path = Path(sys.argv[1] if len(sys.argv) >= 2 else __file__).parent
globalPackagePath: Path = Path(__file__).parent.parent.parent / "lib"

Math: Table = Table(value = {
    String(value = "pi"): Number(value = math.pi), String(value = "e"): Number(value = math.e),
    String(value = "tau"): Number(value = math.tau),
    String(value = "abs"): BuiltinClosure(fn = lambda x: Number(value = abs(x.value))),
    String(value = "floor"): BuiltinClosure(fn = lambda x: Number(value = math.floor(x.value))),
    String(value = "ceil"): BuiltinClosure(fn = lambda x: Number(value = math.ceil(x.value))),
    String(value = "round"): BuiltinClosure(fn = lambda x: Number(value = round(x.value))),
    String(value = "trunc"): BuiltinClosure(fn = lambda x: Number(value = math.trunc(x.value))),
    String(value = "min"): BuiltinClosure(fn = lambda a, b: min(a, b)),
    String(value = "max"): BuiltinClosure(fn = lambda a, b: max(a, b)),
    String(value = "sign"): BuiltinClosure(fn = lambda x: Number(value = math.copysign(1, x.value))),
    String(value = "sin"): BuiltinClosure(fn = lambda x: Number(value = math.sin(x.value))),
    String(value = "cos"): BuiltinClosure(fn = lambda x: Number(value = math.cos(x.value))),
    String(value = "tan"): BuiltinClosure(fn = lambda x: Number(value = math.tan(x.value))),
    String(value = "asin"): BuiltinClosure(fn = lambda x: Number(value = math.asin(x.value))),
    String(value = "acos"): BuiltinClosure(fn = lambda x: Number(value = math.acos(x.value))),
    String(value = "atan"): BuiltinClosure(fn = lambda x: Number(value = math.atan(x.value))),
    String(value = "atan2"): BuiltinClosure(fn = lambda x, y: Number(value = math.atan2(x.value, y.value))),
    String(value = "degrees"): BuiltinClosure(fn = lambda x: Number(value = math.degrees(x.value))),
    String(value = "radians"): BuiltinClosure(fn = lambda x: Number(value = math.radians(x.value))),
    String(value = "exp"): BuiltinClosure(fn = lambda x: Number(value = math.exp(x.value))),
    String(value = "pow"): BuiltinClosure(fn = lambda x, y: Number(value = math.pow(x.value, y.value))),
    String(value = "log"): BuiltinClosure(fn = lambda x, b = Number(value = math.e): Number(value = math.log(x.value, b.value))),
    String(value = "log10"): BuiltinClosure(fn = lambda x: Number(value = math.log10(x.value))),
    String(value = "log2"): BuiltinClosure(fn = lambda x: Number(value = math.log2(x.value))),
    String(value = "hypot"): BuiltinClosure(fn = lambda *x: Number(value = math.hypot(*[i.value for i in x]))),
    String(value = "random"): BuiltinClosure(fn = lambda: Number(value = random.random())),
    String(value = "uniform"): BuiltinClosure(fn = lambda a, b: Number(value = random.uniform(int(a.value), int(b.value)))),
    String(value = "randint"): BuiltinClosure(fn = lambda a, b: Number(value = random.randint(int(a.value), int(b.value)))),
    String(value = "clamp"): BuiltinClosure(fn = lambda a, mmin, mmax: max(mmin, min(a, mmax))),
    String(value = "lerp"): BuiltinClosure(fn = lambda a, b, t: a + (b - a) * t),
    String(value = "eq"): BuiltinClosure(fn = lambda a, b: a == b),
    String(value = "lt"): BuiltinClosure(fn = lambda a, b: a < b),
    String(value = "gt"): BuiltinClosure(fn = lambda a, b: a > b),
    String(value = "le"): BuiltinClosure(fn = lambda a, b: a <= b),
    String(value = "ge"): BuiltinClosure(fn = lambda a, b: a >= b),
    String(value = "neq"): BuiltinClosure(fn = lambda a, b: a != b),
})
Err = Table(value = {
    String(value = "_call_"): BuiltinClosure(fn = lambda typ, message: ValError(typ = typ, value = message)),
    String(value = "panic"): BuiltinClosure(fn = lambda err: Error({}, err.typ, err.value)),
    String(value = "raise"): BuiltinClosure(fn = lambda typ, message: Error({}, typ, message))
})

def read(path: String, isJson = False, lines = False) -> String | Table:
    pth: str = srcPath / path.value
    res: str = ""
    try:
        res = open(pth, "r", encoding = "utf8").read()
        if isJson:
            res = json.loads(res)
    except Exception as e:
        return Error({}, typ = "IOError", value = str(e))
    if not isJson:
        if not lines:
            return String(value = res)
        else:
            rs = Table({})
            for item in res.splitlines():
                rs.append(String(value = item))
            return rs
    else:
        return makeTable(res)
def write(path: String, content: Value, isJson=False, lines=False, append=Number(value=0)) -> Value:
    pth = str(srcPath / path.value)
    if isJson:
        cont = json.dumps(makeObject(content))
    elif lines:
        cont = '\n'.join(content.toList())
    else:
        cont = content.value.replace("\\n", "\n")
    mode = "a" if append.value else "w"
    try:
        with open(pth, mode, encoding="utf8") as f:
            f.write(cont)
    except Exception as e:
        return Error({}, typ = "IOError", value = str(e))
    return content

def exists(path: String) -> Number:
    pth: str = srcPath / path.value
    try:
        return Number(value = int(os.path.exists(pth)))
    except Exception as e:
        return Error({}, typ = "IOError", value = str(e))
def listDir(path: String) -> Table:
    pth: str = srcPath / path.value
    try:
        lis = os.listdir(pth)
    except Exception as e:
        return Error({}, typ = "IOError", value = str(e))
    res = Table({})
    for item in lis:
        res.append(String(value = item))
    return res
def isFile(path: String) -> Number:
    pth: str = srcPath / path.value
    try:
        res = os.path.isfile(pth)
    except Exception as e:
        return Error({}, typ = "IOError", value = str(e))
    return Number(value = int(res))
def isDir(path: String) -> Number:
    pth: str = srcPath / path.value
    try:
        res = os.path.isdir(pth)
    except Exception as e:
        return Error({}, typ = "IOError", value = str(e))
    return Number(value = int(res))
def copy(src: String, dst: String) -> Nil:
    pthSrc: str = srcPath / src
    pthDst: str = srcPath / dst
    try:
        shutil.copy2(pthSrc, pthDst)
    except Exception as e:
        return Error({}, typ = "IOError", value = str(e))
    return Nil()
def move(src: String, dst: String) -> Nil:
    pthSrc: str = srcPath / src
    pthDst: str = srcPath / dst
    try:
        shutil.move(pthSrc, pthDst)
    except Exception as e:
        return Error({}, typ = "IOError", value = str(e))
    return Nil()
def join(table: Table) -> String:
    tab = table.toList()
    try:
        return String(value = os.path.join(tab))
    except Exception as e:
        return Error({}, typ = "IOError", value = str(e))
def findFiles(path: String, check: Value = BuiltinClosure(fn = lambda *args: True)) -> Table:
    pth: str = srcPath / path.value
    try:
        lis = filter(lambda pth: check([String(value = pth)], []), os.listdir(pth))
    except Exception as e:
        return Error({}, typ = "IOError", value = str(e))
    res = Table({})
    for item in lis:
        res.append(String(value = item))
    return res
Fs: Table = Table(value = {
    String(value = "readText"): BuiltinClosure(fn = lambda path: read(path, False)),
    String(value = "writeText"): BuiltinClosure(fn = lambda path, content, append = Number(value = 0): write(path, content, False, append = append)),
    String(value = "readJson"): BuiltinClosure(fn = lambda path: read(path, True)),
    String(value = "writeJson"): BuiltinClosure(fn = lambda path, content, append = Number(value = 0): write(path, content, True, append = append)),
    String(value = "readLines"): BuiltinClosure(fn = lambda path: read(path, False, True)),
    String(value = "writeLines"): BuiltinClosure(fn = lambda path, content, append = Number(value = 0): write(path, content, False, True, append = append)),
    String(value = "exists"): BuiltinClosure(fn = exists),
    String(value = "listDir"): BuiltinClosure(fn = listDir),
    String(value = "isFile"): BuiltinClosure(fn = isFile),
    String(value = "isDir"): BuiltinClosure(fn = isDir),
    String(value = "copy"): BuiltinClosure(fn = copy),
    String(value = "move"): BuiltinClosure(fn = move),
    String(value = "join"): BuiltinClosure(fn = join),
    String(value = "mkdir"): BuiltinClosure(fn = lambda path: (os.mkdir(srcPath / path.value), Nil())[-1]),
    String(value = "rmdir"): BuiltinClosure(fn = lambda path: (os.rmdir(srcPath / path.value), Nil())[-1]),
    String(value = "fileSize"): BuiltinClosure(fn = lambda path: (os.path.getsize(srcPath / path.value, Nil()))[-1]),
    String(value = "findFiles"): BuiltinClosure(fn = findFiles)
})

def encode(res: Table) -> String:
    try:
        return String(value = json.dumps(makeObject(res)))
    except Exception as e:
        return Error({}, typ = "JsonError", value = str(e))
def decode(res: String) -> Table:
    try:
        return makeTable(json.loads(res.value))
    except Exception as e:
        return Error({}, typ = "JsonError", value = str(e))
Json: Table = Table(value = {
    String(value = "encode"): BuiltinClosure(fn = encode),
    String(value = "stringnify"): BuiltinClosure(fn = encode),
    String(value = "decode"): BuiltinClosure(fn = decode),
    String(value = "parse"): BuiltinClosure(fn = decode),
    String(value = "read"): BuiltinClosure(fn = Fs.get(String(value = "readJson"))),
    String(value = "write"): BuiltinClosure(fn = Fs.get(String(value = "writeJson")))
})

def HTTPGet(url: String, params = Nil(), headers = Nil()) -> Table:
    urlString: str = url.value
    try:
        r = requests.get(urlString, params = makeObject(params), headers = makeObject(headers))
    except Exception as e:
        return Error({}, typ = "HTTPError", value = str(e))
    return Table(value = {
        String(value = "status"): Number(value = r.status_code),
        String(value = "headers"): makeTable(dict(r.headers)),
        String(value = "content"): String(value = r.text),
        String(value = 'json'): makeTable(r.json())
    })
def HTTPPost(url: String, data: Table, headers: Table | Nil = Nil()) -> Table:
    urlString = url.value
    try:
        r = requests.post(urlString, json = makeObject(data), headers = makeObject(headers))
    except Exception as e:
        return Error({}, typ = "HTTPError", value = str(e))
    return Table(value = {
        String(value = "status"): Number(value = r.status_code),
        String(value = "headers"): makeTable(dict(r.headers)),
        String(value = "content"): String(value = r.text),
        String(value = "json"): makeTable(r.json())
    })
def HTTPPatch(url: String, data: Table, headers: Table) -> Table:
    urlString = url.value
    try:
        r = requests.patch(urlString, json = makeObject(data), headers = makeObject(headers))
    except Exception as e:
        return Error({}, typ = "HTTPError", value = str(e))
    return Table(value = {
        String(value = "status"): Number(value = r.status_code),
        String(value = "headers"): makeTable(dict(r.headers)),
        String(value = "content"): String(value = r.text)
    })
Http: Table = Table(value = {
    String(value = "get"): BuiltinClosure(fn = HTTPGet),
    String(value = "post"): BuiltinClosure(fn = HTTPPost),
    String(value = "patch"): BuiltinClosure(fn = HTTPPatch)
})

def Run(command: String) -> String:
    try:
        return String(value = subprocess.run(command.value.split(), capture_output = True, text = True).stdout)
    except Exception as e:
        return Error({}, typ = "OSError", value = str(e))
def getEnv(name: String) -> String | Nil:
    envPath = srcPath / ".env"
    for line in open(envPath).readlines():
        k, _, v = line.partition("=")
        if k.strip() == name.value:
            return String(value = v.strip()[1:-1])
    return Nil()
def setEnv(name: String, value: String) -> Nil:
    envPath = srcPath / ".env"
    s = ""
    for line in open(envPath).readlines():
        k, _, v = line.partition("=")
        if k.strip() == name.value:
            s += f"{k} = {value.value}\n"
        else:
            s += f"{k} = {v}\n"
    try:
        open(envPath, "w").write(s)
    except Exception as e:
        return Error({}, typ = "IOError", value = str(e))
    return Nil()
Os: Table = Table(value = {
    String(value = "platform"): BuiltinClosure(fn = lambda: sys.platform),
    String(value = "run"): BuiltinClosure(fn = Run),
    String(value = "shell"): BuiltinClosure(fn = Run),
    String(value = "getEnv"): BuiltinClosure(fn = getEnv),
    String(value = "setEnv"): BuiltinClosure(fn = setEnv)
})

Time: Table = Table(value = {
    String(value = "now"): BuiltinClosure(fn = lambda: Number(value = time.time())),
    String(value = "sleep"): BuiltinClosure(fn = lambda t: [time.sleep(t.value), Nil()][-1])
})

def compose2(f, g) -> Callable:
    return lambda *a, **kw: f([g([*a], kw)], [])
def Compose(*args) -> Callable:
    return BuiltinClosure(fn = functools.reduce(compose2, args))
Func: Table = Table(value = {
    String(value = "compose"): BuiltinClosure(fn = Compose)
})

def measure(fn: Value) -> Number | Error:
    st = time.time()
    res = fn([], [])
    if isinstance(res, Error):
        return res
    ed = time.time()
    return Number(value = ed - st)
def measureMultiple(fn: Value, runs: Number) -> Table | Error:
    tm = []
    for _ in range(runs.value):
        res = measure(fn)
        if isinstance(res, Error):
            return res
        tm.append(res)
    return Table(value = {
        String(value = "mean"): Number(value = statistics.mean(list(map(lambda item: item.value, tm)))),
        String(value = "max"): Number(value = max(list(map(lambda item: item.value, tm)))),
        String(value = "min"): Number(value = min(list(map(lambda item: item.value, tm))))
    })
Benchmark: Table = Table(value = {
    String(value = "measure"): BuiltinClosure(fn = measure),
    String(value = "measureMul"): BuiltinClosure(fn = measureMultiple)
})

conn = None
def sqlInit(path: String) -> Nil:
    global conn
    conn = sqlite3.connect(path.value)
    return Nil()
def sqlExecute(query: String) -> String:
    global conn
    cur = conn.cursor()
    try:
        cur.execute(query.value)
        if cur.description is not None:
            rows = cur.fetchall()
            return String(value = "\n".join(str(row) for row in rows))
        else:
            conn.commit()
            return String(value = "")
    except Exception as e:
        return f"Error: {e}"
    finally:
        cur.close()
Sqlite: Table = Table(value = {
    String(value = "init"): BuiltinClosure(fn = sqlInit),
    String(value = "execute"): BuiltinClosure(fn = sqlExecute)
})

def dynamicImport(file_path: str):
    if not os.path.isfile(file_path):
        return Error({}, typ = "Import Error", value = f"Module file {file_path} not found")
    module_name = os.path.basename(file_path).replace(".py", "")
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module.getGlobal()
cachedModules = {}
def Import(name: String, type: String = String(value = "teeny")) -> Table:
    if type.value == "python":
        mod = importlib.import_module(name.value)
        return makeTable(mod)
    elif type.value == "wrapper":
        mod = dynamicImport(str(srcPath.parent.parent / "lib" / (name.value + ".wrapper.py")))
        return makeTable(mod)
    pth: str = srcPath / name.value
    gPth: str = globalPackagePath / name.value
    if not os.path.isfile(pth):
        pth = pth / "index.ty"
        if not os.path.isfile(pth):
            if not os.path.isfile(gPth):
                gPth = globalPackagePath / name.value / "index.ty"
            if not os.path.isfile(gPth):
                return Error({}, typ = "Import Error", value = f"Module {name.value} not found")
            pth = gPth
    if pth in cachedModules:
        return cachedModules[pth]
    code = open(pth).read()
    from teeny.runner import run
    res = run(code)
    val = res.get("export")
    cachedModules[pth] = val
    return val

def Mix(table: Table, env: Env) -> Nil:
    for key in table.value.keys():
        if isinstance(key, String):
            env.define(key.value, table.get(key))
    return Nil()

def getType(val: Value) -> String:
    if isinstance(val, Number): return String(value = "number")
    if isinstance(val, Table): return String(value = "table")
    if isinstance(val, String): return String(value = "string")
    if isinstance(val, ValError): return String(value = "error")
    if isinstance(val, Closure) or isinstance(val, BuiltinClosure): return String(value = "closure")
    if isinstance(val, Nil): return String(value = "nil")
    return String(value = "unknown")

def Print(*x) -> Nil:
    try:
        for i in x:
            print(makeObject(i.toString()), end = '')
    except Exception as e:
        return Error({}, typ = "IOError", value = str(e))
    return Nil()

def table(*args, **kwargs):
    res = Table()
    res.value = {String(value = k): kwargs[k] for k in kwargs.keys()}
    for i in args:
        res.append(i)
    return res

def evaluate(code: String) -> Value:
    from teeny.runner import run_code
    res = run_code(code.value, print_each = False, print_res = False, is_file = False)
    return res

def makeGlobal() -> Env:
    gEnv = Env()
    gEnv.update({
        "math": Math,
        "print": BuiltinClosure(fn = Print),
        "println": BuiltinClosure(fn = lambda *x: Print(*x, String(value = '\n'))),
        "input": BuiltinClosure(fn = lambda s = String(value = ""): String(value = input(s.value))),
        "export": Table(value = {}),
        "import": BuiltinClosure(fn = lambda x: Import(x)),
        "importPython": BuiltinClosure(fn = lambda x: Import(x, String(value = "wrapper"))),
        "importRaw": BuiltinClosure(fn = lambda x: Import(x, String(value = "python"))),
        "mix": BuiltinClosure(fn = Mix, hasEnv = True),
        "include": BuiltinClosure(fn = lambda name, env: Mix(Import(name), env), hasEnv = True),
        "range": BuiltinClosure(fn = lambda l, r, step = Number(value = 1): makeTable(list(range(int(l.value), int(r.value), int(step.value))))),
        "error": Err,
        "fs": Fs,
        "json": Json,
        "http": Http,
        "os": Os,
        "time": Time,
        "argv": makeTable(sys.argv[1:]),
        "func": Func,
        "benchmark": Benchmark,
        "sql": Sqlite,
        "type": BuiltinClosure(fn = getType),
        "copy": BuiltinClosure(fn = copy),
        "string": BuiltinClosure(fn = lambda x: x.toString()),
        "number": BuiltinClosure(fn = lambda x: x.toNumber()),
        "table": BuiltinClosure(fn = table),
        "bool": BuiltinClosure(fn = lambda x: isTruthy(x)),
        "eval": BuiltinClosure(fn = evaluate)
    })
    return gEnv