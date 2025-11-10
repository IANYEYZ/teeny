from teeny.value import Env, Number, String, Table, Error, ValError, BuiltinClosure, \
                        makeTable, makeObject, Value, Nil, Closure, copy
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

srcPath = Path(sys.argv[1] if len(sys.argv) >= 2 else __file__).parent

Math = Table(value = {
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
        res = open(pth, "r").read()
        if isJson:
            res = json.loads(res)
    except Exception as e:
        print(e)
        return Error({}, "IOError", "Error when reading from file")
    if not isJson:
        if not lines:
            return String(res)
        else:
            rs = Table({})
            for item in res.splitlines():
                rs.append(String(value = item))
            return rs
    else:
        return makeTable(res)
def write(path: String, content: Value, isJson = False, lines = False, append = Number(value = 0)) -> Value:
    pth: str = srcPath / path.value
    cont: str = (content.value if not lines else '\n'.join(content.toList())) if not isJson else json.dumps(makeObject(content))
    num: bool = bool(append.value)
    try:
        open(pth, ("w" if not num else "a")).write(cont)
    except:
        return Error({}, "IOError", "Error when writing to file")
    return content
def exists(path: String) -> Number:
    pth: str = srcPath / path.value
    return Number(value = int(os.path.exists(pth)))
def listDir(path: String) -> Table:
    pth: str = srcPath / path.value
    lis = os.listdir(pth)
    res = Table({})
    for item in lis:
        res.append(String(value = item))
    return res
def isFile(path: String) -> Number:
    pth: str = srcPath / path.value
    res = os.path.isfile(pth)
    return Number(value = int(res))
def isDir(path: String) -> Number:
    pth: str = srcPath / path.value
    res = os.path.isdir(pth)
    return Number(value = int(res))
def copy(src: String, dst: String) -> Nil:
    pthSrc: str = srcPath / src
    pthDst: str = srcPath / dst
    shutil.copy2(pthSrc, pthDst)
    return Nil()
def move(src: String, dst: String) -> Nil:
    pthSrc: str = srcPath / src
    pthDst: str = srcPath / dst
    shutil.move(pthSrc, pthDst)
    return Nil()
def join(table: Table) -> String:
    tab = table.toList()
    return String(value = os.path.join(tab))
def findFiles(path: String, check: Value) -> Table:
    pth: str = srcPath / path
    lis = os.listdir(pth)
    lis = filter(check, lis)
    res = Table({})
    for item in lis:
        res.append(String(value = item))
    return res
Fs = Table(value = {
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
    return String(value = json.dumps(makeObject(res)))
def decode(res: String) -> Table:
    return makeTable(json.loads(res.value))
Json = Table(value = {
    String(value = "encode"): BuiltinClosure(fn = encode),
    String(value = "stringnify"): BuiltinClosure(fn = encode),
    String(value = "decode"): BuiltinClosure(fn = decode),
    String(value = "parse"): BuiltinClosure(fn = decode),
    String(value = "read"): BuiltinClosure(fn = Fs.get(String(value = "readJson"))),
    String(value = "write"): BuiltinClosure(fn = Fs.get(String(value = "writeJson")))
})

def HTTPGet(url: String, params = Nil()):
    urlString: str = url.value
    r = requests.get(urlString, makeObject(params))
    return Table(value = {
        String(value = "status"): Number(value = r.status_code),
        String(value = "headers"): makeTable(dict(r.headers)),
        String(value = "content"): String(value = r.text)
    })
def HTTPPost(url: String, data: Table):
    urlString = url.value
    r = requests.post(urlString, json = makeObject(data))
    return Table(value = {
        String(value = "status"): Number(value = r.status_code),
        String(value = "headers"): makeTable(dict(r.headers)),
        String(value = "content"): String(value = r.text)
    })
Http = Table(value = {
    String(value = "get"): BuiltinClosure(fn = HTTPGet),
    String(value = "post"): BuiltinClosure(fn = HTTPPost)
})

def Run(command: String):
    return String(value = subprocess.run(command.value.split(), capture_output = True, text = True).stdout)
def getEnv(name: String) -> String | Nil:
    envPath = srcPath / ".env"
    for line in open(envPath).readlines():
        k, _, v = line.partition("=")
        if k.strip() == name.value:
            return String(value = v.strip())
    return Nil()
Os = Table(value = {
    String(value = "platform"): BuiltinClosure(fn = lambda: sys.platform),
    String(value = "run"): BuiltinClosure(fn = Run),
    String(value = "shell"): BuiltinClosure(fn = Run),
    String(value = "getEnv"): BuiltinClosure(fn = getEnv),
    String(value = "setEnv"): BuiltinClosure(fn = lambda name, val: [os.setenv(name.value, val.value), Nil()][-1])
})

Time = Table(value = {
    String(value = "now"): BuiltinClosure(fn = lambda: Number(value = time.time())),
    String(value = "sleep"): BuiltinClosure(fn = lambda t: [time.sleep(t.value), Nil()][-1])
})

def compose2(f, g):
    return lambda *a, **kw: f([g([*a], kw)], {})
def Compose(*args):
    return BuiltinClosure(fn = functools.reduce(compose2, args))
def Pipe(*args):
    pass
Func = Table(value = {
    String(value = "compose"): BuiltinClosure(fn = Compose)
})

def measure(fn: Value):
    st = time.time()
    fn([], {})
    ed = time.time()
    return Number(value = ed - st)
def measureMultiple(fn: Value, runs: Number):
    tm = []
    for _ in range(runs.value):
        tm.append(measure(fn))
    return Table(value = {
        String(value = "mean"): Number(value = statistics.mean(list(map(lambda item: item.value, tm)))),
        String(value = "max"): Number(value = max(list(map(lambda item: item.value, tm)))),
        String(value = "min"): Number(value = min(list(map(lambda item: item.value, tm))))
    })
Benchmark = Table(value = {
    String(value = "measure"): BuiltinClosure(fn = measure),
    String(value = "measureMul"): BuiltinClosure(fn = measureMultiple)
})

def Import(name: String) -> Table:
    code = open(srcPath / name.value).read()
    from teeny.runner import run
    res = run(code)
    val = res.get("export")
    return val

def Mix(table: Table, env: Env):
    for key in table.value.keys():
        if isinstance(key, String):
            env.define(key.value, table.get(key))

def getType(val: Value) -> String:
    if isinstance(val, Number): return String(value = "number")
    if isinstance(val, Table): return String(value = "table")
    if isinstance(val, String): return String(value = "string")
    if isinstance(val, ValError): return String(value = "error")
    if isinstance(val, Closure) or isinstance(val, BuiltinClosure): return String(value = "closure")
    if isinstance(val, Nil): return String(value = "nil")

def Print(*x) -> Nil:
    for i in x:
        print(makeObject(i), end = '')
    return Nil()

def makeGlobal() -> Env:
    gEnv = Env()
    gEnv.update({
        "math": Math,
        "print": BuiltinClosure(fn = Print),
        "println": BuiltinClosure(fn = lambda *x: Print(*x, String(value = '\n'))),
        "input": BuiltinClosure(fn = lambda: String(value = input(""))),
        "export": Table(value = {}),
        "import": BuiltinClosure(fn = Import),
        "mix": BuiltinClosure(fn = Mix, hasEnv = True),
        "include": BuiltinClosure(fn = lambda name, env: Mix(Import(name), env), hasEnv = True),
        "range": BuiltinClosure(fn = lambda l, r, step = Number(value = 1): makeTable(list(range(l.value, r.value, step.value)))),
        "error": Err,
        "fs": Fs,
        "json": Json,
        "http": Http,
        "os": Os,
        "time": Time,
        "argv": sys.argv[1:],
        "func": Func,
        "benchmark": Benchmark,
        "type": BuiltinClosure(fn = getType),
        "copy": BuiltinClosure(fn = copy)
    })
    return gEnv