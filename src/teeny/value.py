from dataclasses import dataclass, field
from typing import Optional, Callable
from teeny.AST import AST
from teeny.exception import RuntimeError
import math
import functools
import codecs
import uuid
from collections.abc import Callable
from typing import Union

def requireType(message: str) -> Callable:
    def decorator(func) -> Callable:
        @functools.wraps(func)
        def inner(*args, **kwargs):
            hints = func.__annotations__
            for name, hint in hints.items():
                if name == 'return':
                    continue
                value = kwargs.get(name, None)
                if value is None and name in func.__code__.co_varnames:
                    idx = func.__code__.co_varnames.index(name)
                    if idx < len(args):
                        value = args[idx]
                if isinstance(hint, str):
                    hint = globals().get(hint)
                if not isinstance(value, hint):
                    return Error(typ = "Runtime Error", value = message)
            return func(*args, **kwargs)
        return inner
    return decorator


@dataclass
class Value:
    metaTable: dict["Value": "Value"] = field(default_factory=dict)
    gID: str = field(default_factory=str)

    def __post_init__(self) -> None:
        self.gID = str(uuid.uuid4())
    def register(self, pos: "Value", val: "Value") -> None:
        self.metaTable[pos] = val
    def get(self, pos: "Value") -> "Value":
        return self.metaTable.get(pos, Nil())
    def toString(self) -> "String":
        return String(value = "value")
    def toNumber(self) -> "Error":
        return Error(typ = "Runtime Error", value = "convert non-Number to Number")
    def fact(self) -> "Error":
        return Error(typ = "Runtime Error", value = "calculate factorial for non-Number")
    def negative(self) -> "Error":
        return Error(typ = "Runtime Error", value = "calculate negative for non-Number")

@dataclass
class Number(Value):
    value: float = 0.0

    def __post_init__(self) -> None:
        super().__post_init__()
        self.register(String(value = "times"), BuiltinClosure(fn = self.times))

    @requireType("add a non-Number to a Number")
    def __add__(self, rhs: "Number") -> "Number":
        return Number(value = self.value + rhs.value)
    @requireType("minus a non-Number from a Number")
    def __sub__(self, rhs: "Number") -> "Number":
        return Number(value = self.value - rhs.value)
    @requireType("multiply a non-Number with a Number")
    def __mul__(self, rhs: "Number") -> "Number":
        return Number(value = self.value * rhs.value)
    @requireType("divide a non-Number from a Number")
    def __truediv__(self, rhs: "Number") -> "Number":
        if rhs.value == 0: return Error(typ = "Runtime Error", value = "divide by zero")
        return Number(value = self.value / rhs.value)
    @requireType("divide a non-Number from a Number")
    def __floordiv__(self, rhs: "Number") -> "Number":
        return Number(value = self.value / rhs.value)
    @requireType("mod a non-Number from a Number")
    def __mod__(self, rhs: "Number") -> "Number":
        return Number(value = self.value % rhs.value)
    def __eq__(self, rhs: Value) -> "Number":
        if not isinstance(rhs, Number): return Number(value = 0)
        return Number(value = int(self.value == rhs.value))
    def __ne__(self, rhs: Value) -> "Number":
        if not isinstance(rhs, Number): return Number(value = 1)
        return Number(value = int(self.value != rhs.value))
    @requireType("compare between non-Number and Number")
    def __gt__(self, rhs: "Number") -> "Number":
        return Number(value = int(self.value > rhs.value))
    @requireType("compare between non-Number and Number")
    def __ge__(self, rhs: "Number") -> "Number":
        return Number(value = int(self.value >= rhs.value))
    @requireType("compare between non-Number and Number")
    def __lt__(self, rhs: "Number") -> "Number":
        return Number(value = int(self.value < rhs.value))
    @requireType("compare between non-Number and Number")
    def __le__(self, rhs: "Number") -> "Number":
        return Number(value = int(self.value <= rhs.value))
    def __hash__(self) -> int:
        return self.value.__hash__()
    def __bool__(self) -> bool:
        return isTruthy(self)
    
    def negative(self) -> "Number":
        return Number(value = -self.value)
    def times(self) -> "Table":
        return makeTable(list(range(0, int(self.value))))
    def fact(self) -> "Number":
        return Number(value = math.factorial(int(self.value)))
    def toString(self) -> "String":
        return String(value = str(makeObject(self)))
    def toNumber(self) -> "Number":
        return self

@dataclass
class String(Value):
    value: str = ""
    noConstruct: bool = False

    def __post_init__(self) -> None:
        if self.noConstruct:
            return
        super().__post_init__()
        self.register(String(value = "len", noConstruct = True), BuiltinClosure(fn = self.len))
        self.register(String(value = "slice", noConstruct = True), BuiltinClosure(fn = self.slice))
        self.register(String(value = "find", noConstruct = True), BuiltinClosure(fn = self.find))
        self.register(String(value = "upper", noConstruct = True), BuiltinClosure(fn = self.upper))
        self.register(String(value = "lower", noConstruct = True), BuiltinClosure(fn = self.lower))
        self.register(String(value = "cap", noConstruct = True), BuiltinClosure(fn = self.cap))
        self.register(String(value = "trim", noConstruct = True), BuiltinClosure(fn = self.trim))
        self.register(String(value = "split", noConstruct = True), BuiltinClosure(fn = self.split))
        self.register(String(value = "join", noConstruct = True), BuiltinClosure(fn = self.join))
        self.register(String(value = "format", noConstruct = True), BuiltinClosure(fn = self.format))

    @requireType("add a non-String to a String")
    def __add__(self, rhs: "String") -> "String":
        return String(value = self.value + rhs.value)
    @requireType("multiply a non-Number to a String")
    def __mul__(self, rhs: Number) -> "String":
        return String(value = self.value * int(rhs.value))
    def __eq__(self, rhs: Value) -> Number:
        if not isinstance(rhs, String): return Number(value = 0)
        return Number(value = self.value == rhs.value)
    def __ne__(self, rhs: Value) -> Number:
        if not isinstance(rhs, String): return Number(value = 1)
        return Number(value = self.value != rhs.value)
    @requireType("compare between non-String and String")
    def __gt__(self, rhs: "String") -> Number:
        return Number(value = self.value > rhs.value)
    @requireType("compare between non-String and String")
    def __ge__(self, rhs: "String") -> Number:
        return Number(value = self.value >= rhs.value)
    @requireType("compare between non-String and String")
    def __lt__(self, rhs: "String") -> Number:
        return Number(value = self.value < rhs.value)
    @requireType("compare between non-String and String")
    def __le__(self, rhs: "String") -> Number:
        return Number(value = self.value <= rhs.value)
    def __hash__(self) -> int:
        return self.value.__hash__()
    
    def get(self, pos: Value) -> Value:
        if isinstance(pos, Number):
            return String(value = self.value[int(pos.value)])
        else:
            return super().get(pos)
    def set(self, pos: Value, val: Value) -> Union["Error", "Nil"]:
        if not isinstance(pos, Number) or not isinstance(val, String):
            return Error(typ = "Runtime Error", value = "index string with non-Number")
        v = list(self.value); v[int(pos.value)] = val.value
        self.value = "".join(v)
        return Nil()
    
    def len(self) -> Number:
        return Number(value = len(self.value))
    def slice(self, l: Number, r: Number) -> "String":
        return String(value = self.value[int(l.value):int(r.value) + 1])
    def find(self, sub: "String") -> Number:
        return Number(value = self.value.find(sub.value))
    def upper(self) -> "String":
        return String(value = self.value.upper())
    def lower(self) -> "String":
        return String(value = self.value.lower())
    def cap(self) -> "String":
        return String(value = self.value.capitalize())
    def trim(self) -> "String":
        return String(value = self.value.strip())
    def split(self, sep: "String") -> "Table":
        return makeTable(self.value.split(sep.value))
    def join(self, tab: "Table") -> "String":
        return String(value = self.value.join(makeObject(tab)))
    def format(self, tab: "Table") -> "String":
        return String(value = self.value.format(*makeObject(tab.toList()), **makeObject(tab.toDict())))
    def toString(self) -> "String":
        return self
    def toNumber(self) -> "Number":
        res = None
        try:
            res = Number(value = float(self.value))
        except ValueError:
            res = Error(typ = "Runtime Error", value = "convert non-Number to Number")
        return res

@dataclass
class Table(Value):
    value: dict[Value: Value] = field(default_factory=dict)
    size: int = 0

    def __post_init__(self) -> None:
        super().__post_init__()
        self.register(String(value = "push"), BuiltinClosure(fn = self.append))
        self.register(String(value = "keys"), BuiltinClosure(fn = self.keys))
        self.register(String(value = "values"), BuiltinClosure(fn = self.values))
        self.register(String(value = "pairs"), BuiltinClosure(fn = self.pairs))
        self.register(String(value = "mean"), BuiltinClosure(fn = lambda: makeTable(self.mean())))
        self.register(String(value = "sum"), BuiltinClosure(fn = lambda: makeTable(self.sum())))
        self.register(String(value = "median"), BuiltinClosure(fn = lambda: makeTable(self.median())))
        self.register(String(value = "stdev"), BuiltinClosure(fn = lambda: makeTable(self.stdev())))
        self.register(String(value = "describe"), BuiltinClosure(fn = lambda: makeTable(self.describe())))
        self.register(String(value = "has"), BuiltinClosure(fn = self.has))
        self.register(String(value = "map"), BuiltinClosure(fn = self.map))
        self.register(String(value = "sort"), BuiltinClosure(fn = lambda: self.sort()))
        self.register(String(value = "filter"), BuiltinClosure(fn = self.filter))
        self.register(String(value = "_iter_"), BuiltinClosure(fn = self._iter_))

    @requireType("add a non-Table to a Table")
    def __add__(self, rhs: "Table") -> "Table":
        l = self.toList() + rhs.toList()
        return Table(value = {**{Number(value = pos): v for pos, v in enumerate(l)}, **self.toDict(), **rhs.toDict()}, size = len(l))
    def __eq__(self, rhs: "Value") -> Number:
        if not isinstance(rhs, Table): return Number(value = 0)
        return Number(value = int(self.value == rhs.value))
    def __ne__(self, rhs: "Value") -> Number:
        if not isinstance(rhs, Table): return Number(value = 1)
        return Number(value = int(self.value != rhs.value))
    def __call__(self, value, kwarg) -> Value:
        return self.get(String(value = "_call_"))(value, kwarg)
    
    def append(self, val: Value) -> Value:
        self.value[Number(value = self.size)] = val
        self.size += 1
        return val
    def update(self, val: dict) -> None:
        self.value.update(val)
    def get(self, pos: Value) -> Value:
        res = self.value.get(pos, Nil())
        if not isinstance(res, Nil):
            return res
        return super().get(pos)
    def set(self, pos: Value, val: Value) -> Value:
        if self.value.get(pos) == None:
            return Error(typ = "Runtime Error", value = "setting non-existing property")
        self.value[pos] = val
        return val
    def define(self, pos: Value, val: Value) -> Value:
        self.value[pos] = val
        return val
    def keys(self) -> "Table":
        res = Table()
        for k in self.value.keys():
            res.append(k)
        return res
    def values(self) -> "Table":
        res = Table()
        for k in self.value.keys():
            res.append(self.value[k])
        return res
    def pairs(self) -> "Table":
        res = Table()
        for k in self.value.keys():
            res.append(Table(value = {Number(value = 0): k, Number(value = 1): self.value[k]}, size = 2))
        return res
    def toList(self) -> list:
        res = []
        for k in self.value.keys():
            if isinstance(k, Number):
                res.append(self.value.get(k))
        return res
    def toDict(self) -> dict:
        res = {}
        for k in self.value.keys():
            if not isinstance(k, Number):
                res[k] = self.value.get(k)
        return res
    def map(self, fn) -> "Table":
        res = Table({})
        for k in self.value.keys():
            res.define(k, fn([self.value.get(k), k], {}))
        return res
    def filter(self, fn) -> "Table":
        res = Table({})
        l = self.toList(); d = self.toDict()
        for p, v in enumerate(l):
            if isTruthy(fn([v, Number(value = p)], {})):
                res.append(v)
        for k in d.keys():
            if isTruthy(fn([d.get(k), k], {})):
                res.define(k, d.get(k))
        return res
    def sum(self) -> float:
        return sum(self.toList(), Number(value = 0)).value
    def mean(self) -> float:
        return (sum(self.toList(), Number(value = 0)) / Number(value = len(self.toList()))).value
    def median(self) -> float:
        lis = self.toList()
        lis.sort()
        if len(lis) % 2 == 1:
            return lis[len(lis) // 2].value
        else:
            return ((lis[len(lis) // 2] + lis[len(lis) // 2 - 1]) / Number(value = 2)).value
    def stdev(self) -> float:
        avg = self.mean()
        arr = list(map(lambda x: (x - avg) ** 2, makeObject(self.toList())))
        return math.sqrt(sum(arr) / len(arr))
    def describe(self):
        return {
            "sum": self.sum(),
            "mean": self.mean(),
            "median": self.median(),
            "stdev": self.stdev()
        }
    def sort(self) -> "Table":
        l = self.toList()
        l.sort()
        res = Table({})
        res.value = self.toDict()
        for i in l:
            res.append(i)
        return res
    def has(self, key: Value) -> Number:
        if not isinstance(self.get(key), Nil):
            return Number(value = 1)
        else:
            return Number(value = 0)
    def lPair(self) -> "Table":
        l = self.toList()
        res = Table()
        for pos, i in enumerate(l):
            if pos < len(l) - 1:
                tab = Table(); tab.append(i); tab.append(l[pos + 1])
                res.append(tab)
        return res
    def toString(self) -> "String":
        l = self.toList(); d = self.toDict()
        parts = []
        for item in l:
            s = item.toString().value
            parts.append(s)
        for k, v in d.items():
            ks = k.toString().value
            vs = v.toString().value
            parts.append(f"{ks}: {vs}")
        return String(value = "[" + ", ".join(parts) + "]")
    def toNumber(self) -> "Number":
        return Error(typ = "Runtime Error", value = "convert non-Number to Number")
    def _iter_(self, val = [], kw = {}) -> Callable:
        # Default iterative protocol
        cur = 0
        end = self.size
        def nxt(val = [], kw = {}) -> Union[Number, "Nil"]:
            nonlocal cur
            if cur < end:
                cur += 1
                return Number(value = cur - 1)
            else:
                return Nil()
        return nxt

class Env(dict):
    def __init__(self, outer: Optional["Env"] = None) -> None:
        self.outer = outer
    
    def read(self, name: str) -> Value:
        if self.get(name) != None:
            return self.get(name)
        else:
            if self.outer == None:
                return Error(typ = "Runtime Error", value = f"read from non-existing variable")
            return self.outer.read(name)
    
    def write(self, name: str, val: Value) -> Value:
        if self.get(name, None) != None:
            self[name] = val
            return val
        else:
            if self.outer == None:
                return Error(typ = "Runtime Error", value = f"assign to non-existing variable")
            return self.outer.write(name, val)
    
    def define(self, name: str, val: Value) -> Value:
        self.update({name: val})
        return val
@dataclass
class Closure:
    params: list[str] = field(default_factory = list)
    default: list[list[Value]] = field(default_factory = list)
    implementation: list[AST] = field(default_factory = list)
    env: "Env" = field(default_factory = Env)
    isDynamic: bool = False
    gID: str = ""

    def __init__(self, params: list[str], implementation: AST, env: Env, isDynamic: bool) -> None:
        self.params = []
        self.default = []
        for item in params:
            if isinstance(item, list):
                self.params.append(item[0])
                self.default.append(item)
            else:
                self.params.append(item)
        self.implementation = implementation; self.env = snapshot(env) if isDynamic else env;
        self.isDynamic = isDynamic
        self.gID = str(uuid.uuid4())

    def __eq__(self, rhs) -> Number:
        if not isinstance(rhs, Closure): return Number(value = 0)
        return Number(value = int(self.gID == rhs.gID))
    def __ne__(self, rhs) -> Number:
        if not isinstance(rhs, Closure): return Number(value = 1)
        return Number(value = int(self.gID != rhs.gID))

    def __call__(self, value, kwarg: list) -> Value:
        nEnv = Env(outer = self.env)
        for pos in range(len(self.default)):
            param = self.default[pos][0]
            dVal = self.default[pos][1]
            from teeny.interpreter import assignVariable
            assignVariable(param, dVal, nEnv, True, False)
        if len(value) > len(self.params):
            value = value[0:len(self.params)]
        for pos, param in enumerate(self.params):
            from teeny.interpreter import assignVariable
            if pos < len(value):
                assignVariable(param, value[pos], nEnv, True, False)
        for pos, param in enumerate(kwarg):
            from teeny.interpreter import assignVariable
            assignVariable(param[0], param[1], nEnv, True, False)
        nEnv.define("this", self)
        # nEnv.define("n", value[0])
        lst = None
        for ast in self.implementation:
            from teeny.interpreter import interpret
            lst = interpret(ast, nEnv)
        return lst
    def toString(self) -> "String":
        return String(value = "Closure")
    def toNumber(self) -> "Number":
        return Error(typ = "Runtime Error", value = "convert non-Number to Number")

@dataclass
class Error(Value):
    typ: str = ""
    value: str = ""

    def __post_init__(self) -> None:
        super().__post_init__()
        self.register(String(value = "type"), String(value = self.typ))
        self.register(String(value = "value"), String(value = self.value))
    
    def __eq__(self, rhs) -> Number:
        if not isinstance(rhs, Error):
            return Number(value = 0)
        return Number(value = int(self.typ == rhs.typ and self.value == rhs.value))
    def __ne__(self, rhs) -> Number:
        if not isinstance(rhs, Error):
             return Number(value = 1)
        return Number(value = int(self.typ != rhs.typ or self.value != rhs.value))
    def toString(self) -> "String":
        return String(value = f"Error({self.typ}, {self.value})")
    def toNumber(self) -> "Number":
        return Error(typ = "Runtime Error", value = "convert non-Number to Number")

@dataclass
class ValError(Value):
    typ: str = ""
    value: str = ""

    def __post_init__(self) -> None:
        super().__post_init__()
        self.register(String(value = "type"), self.typ)
        self.register(String(value = "value"), self.value)
    
    def __eq__(self, rhs) -> Number:
        if not isinstance(rhs, Error):
            return Number(value = 0)
        return Number(value = int(self.typ == rhs.typ and self.value == rhs.value))
    def __ne__(self, rhs) -> Number:
        if not isinstance(rhs, Error):
             return Number(value = 1)
        return Number(value = int(self.typ != rhs.typ or self.value != rhs.value))
    def toString(self) -> "String":
        return String(value = f"Error({self.typ}, {self.value})")
    def toNumber(self) -> "Number":
        return Error(typ = "Runtime Error", value = "convert non-Number to Number")

@dataclass
class Nil(Value):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Nil, cls).__new__(cls)
        return cls.instance
    def toString(self) -> "String":
        return String(value = "nil")
    def toNumber(self) -> "Number":
        return Error(typ = "Runtime Error", value = "convert non-Number to Number")

@dataclass
class BuiltinClosure(Value):
    fn: Callable = lambda: Number(value = 0)
    hasEnv: bool = False

    def __call__(self, value: list, kwarg: list = []) -> Value:
        kwarg_dict = {}
        for item in kwarg:
            if item[0].typ == "NAME":
                kwarg_dict[item[0].value] = item[1]
        return self.fn(*value, **kwarg_dict)
@dataclass
class BuiltinValue(Value):
    value: Value = field(default_factory = Nil)

@dataclass
class Underscore(Value):
    pass

def snapshot(e: Env) -> Env:
    if e.outer == None:
        res = Env(None)
        res.update(e.copy())
        return res
    else:
        res = Env(snapshot(e.outer))
        res.update(e.copy())
        return res

def isTruthy(value: Value) -> bool:
    if isinstance(value, Number):
        return bool(value.value)
    elif isinstance(value, String):
        return bool(len(value.value) > 0)
    elif isinstance(value, Table):
        return bool(len(value.value.keys()) > 0)
    elif isinstance(value, Closure) or isinstance(value, BuiltinClosure):
        return True
    elif isinstance(value, Nil):
        return False
    elif isinstance(value, BuiltinValue):
        return isTruthy(value.value)
    else:
        return False

def makeTable(value: list | dict | str | int | bool | float | None) -> Value:
    if isinstance(value, int): return Number(value = value)
    elif isinstance(value, str): return String(value = value)
    elif isinstance(value, bool): return Number(value = int(value))
    elif isinstance(value, float): return Number(value = value)
    elif isinstance(value, list):
        res = Table({})
        for item in value:
            res.append(makeTable(item))
        return res
    elif isinstance(value, dict):
        res = Table({})
        for item in value.keys():
            res.define(makeTable(item), makeTable(value.get(item)))
        return res
    elif value == None:
        return Nil()

def makeObject(value: Value | dict | list) -> list | dict | str | int | bool | None:
    if isinstance(value, Number):
        if int(value.value) == value.value: return int(value.value)
        return value.value
    elif isinstance(value, String): return value.value.encode().decode("unicode_escape")
    elif isinstance(value, Underscore): return "_"
    elif isinstance(value, Table):
        isList = True
        for i in value.value.keys():
            if not isinstance(i, Number):
                isList = False
        if isList:
            res = []
            for i in value.value.values():
                res.append(makeObject(i))
            return res
        else:
            res = {}
            for i in value.value.keys():
                res.update({str(makeObject(i)): makeObject(value.value.get(i))})
            return res
    elif isinstance(value, Nil):
        return None
    elif isinstance(value, Closure):
        return "Closure"
    elif isinstance(value, Error) or isinstance(value, ValError):
        return str({"type": value.typ, "value": value.value})
    elif isinstance(value, dict):
        res = {}
        for k in value.keys():
            res[k] = makeObject(value.get(k))
        return res
    elif isinstance(value, list):
        res = []
        for v in value:
            res.append(makeObject(v))
        return res
def match(l: Union[Value, AST], r: Value, env: Env) -> bool:
    if isinstance(l, Value):
        if isinstance(l, Underscore):
            return True
        elif isinstance(l, Number): return isTruthy(l == r)
        elif isinstance(l, String): return isTruthy(l == r)
        elif isinstance(l, Table):
            if not isinstance(r, Table): return False
            for k in l.value.keys():
                if r.value.get(k) == None: return False
                if not match(l.get(k), r.get(k), env): return False
            return True
    else:
        if l.value == "||":
            return match(l.children[0], r, env) or match(l.children[1], r, env)
        elif l.value == "&&":
            return match(l.children[0], r, env) and match(l.children[1], r, env)
        elif l.value == "!":
            return not match(l.children[0], r, env)
        elif l.typ == "FN" or l.typ == "FN-DYNAMIC":
            from teeny.interpreter import interpret
            return isTruthy(interpret(l, env)([r], {}))
        else:
            from teeny.interpreter import interpret
            return match(interpret(l, env), r, env)

def copy(v: Value) -> Value:
    if isinstance(v, Number):
        return Number(value = v.value)
    elif isinstance(v, String):
        return String(value = v.value)
    elif isinstance(v, Nil):
        return Nil()
    elif isinstance(v, Table):
        res = Table()
        for k in v.value.keys():
            res.set(copy(k), copy(v.value.get(k)))
        return res