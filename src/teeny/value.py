from dataclasses import dataclass, field
from typing import Optional, Callable
from teeny.AST import AST
from teeny.exception import RuntimeError
import math

@dataclass
class Value:
    metaTable: dict["Value": "Value"] = field(default_factory=dict)

    def register(self, pos: "Value", val: "Value"):
        self.metaTable[pos] = val
    def get(self, pos: "Value") -> "Value":
        return self.metaTable.get(pos, Nil())

    def __and__(self, rhs) -> "Number":
        return Number(isTruthy(self) and isTruthy(rhs))
    def __or__(self, rhs) -> "Number":
        return Number(isTruthy(self) or isTruthy(rhs))
    def __not__(self) -> "Number":
        return Number(not isTruthy(self))

@dataclass
class Number(Value):
    value: int = 0

    def __post_init__(self):
        self.register(String(value = "times"), BuiltinClosure(fn = self.times))

    def __add__(self, rhs) -> "Number":
        return Number(value = self.value + rhs.value)
    def __sub__(self, rhs) -> "Number":
        return Number(value = self.value - rhs.value)
    def __mul__(self, rhs) -> "Number":
        return Number(value = self.value * rhs.value)
    def __div__(self, rhs) -> "Number":
        return Number(value = self.value / rhs.value)
    def __mod__(self, rhs) -> "Number":
        return Number(value = self.value % rhs.value)
    def __eq__(self, rhs) -> "Number":
        if not isinstance(rhs, Number): return Number(value = 0)
        return Number(value = int(self.value == rhs.value))
    def __neq__(self, rhs) -> "Number":
        if not isinstance(rhs, Number): return Number(value = 1)
        return Number(value = int(self.value != rhs.value))
    def __gt__(self, rhs) -> "Number":
        return Number(value = int(self.value > rhs.value))
    def __ge__(self, rhs) -> "Number":
        return Number(value = int(self.value >= rhs.value))
    def __lt__(self, rhs) -> "Number":
        return Number(value = int(self.value < rhs.value))
    def __le__(self, rhs) -> "Number":
        return Number(value = int(self.value <= rhs.value))
    def __hash__(self) -> int:
        return self.value.__hash__()
    def __bool__(self) -> bool:
        return isTruthy(self)
    
    def negative(self) -> "Number":
        return Number(value = -self.value)
    def times(self) -> "Table":
        return makeTable(range(0, self.value))

@dataclass
class String(Value):
    value: str = ""
    noConstruct: bool = False

    def __post_init__(self):
        if self.noConstruct:
            return
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

    def __add__(self, rhs) -> "String":
        return String(value = self.value + rhs.value)
    def __eq__(self, rhs) -> Number:
        if not isinstance(rhs, String): return Number(value = 0)
        return Number(value = self.value == rhs.value)
    def __neq__(self, rhs) -> Number:
        if not isinstance(rhs, String): return Number(value = 1)
        return Number(value = self.value != rhs.value)
    def __gt__(self, rhs) -> Number:
        return Number(value = self.value > rhs.value)
    def __ge__(self, rhs) -> Number:
        return Number(value = self.value >= rhs.value)
    def __lt__(self, rhs) -> Number:
        return Number(value = self.value < rhs.value)
    def __le__(self, rhs) -> Number:
        return Number(value = self.value <= rhs.value)
    def __hash__(self) -> int:
        return self.value.__hash__()
    
    def get(self, pos: Value):
        if isinstance(pos, Number):
            return self.value[pos.value]
        else:
            return super().get(pos)
    def set(self, pos: Value, val: Value):
        if not isinstance(pos, Number) or not isinstance(val, String):
            raise RuntimeError("String is only indexable with Number")
        self.value[pos] = val.value
    
    def len(self) -> Number:
        return Number(value = len(self.value))
    def slice(self, l: Number, r: Number) -> "String":
        return String(value = self.value[l.value:r.value])
    def find(self, sub: "String") -> Number:
        return Number(value = self.value.find(sub.value))
    def upper(self) -> "String":
        return String(value = self.value.upper())
    def lower(self) -> "String":
        return String(value = self.value.lower())
    def cap(self) -> "String":
        return String(value = self.value.capitalize())
    def trim(self) -> "String":
        return String(value = self.trim())
    def split(self, sep: "String") -> "Table":
        return makeTable(self.value.split(sep.value))
    def join(self, tab: "Table") -> "String":
        return self.value.join(makeObject(tab))
    def format(self, tab: "Table") -> "String":
        return self.value.format(*tab.toList(), **tab.toDict())

@dataclass
class Table(Value):
    value: dict[Value: Value] = field(default_factory=dict)
    size: int = 0

    def __post_init__(self):
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
        self.register(String(value = "filter"), BuiltinClosure(fn = self.filter))
        self.register(String(value = "_iter_"), BuiltinClosure(fn = self._iter_))

    def __add__(self, rhs: "Table") -> "Table":
        return Table(value = {**self.value, **rhs.value})
    def __eq__(self, rhs) -> Number:
        if not isinstance(rhs, Table): return Number(value = 0)
        return Number(value = int(self.value == rhs.value))
    def __neq__(self, rhs) -> Number:
        if not isinstance(rhs, Table): return Number(value = 1)
        return Number(value = int(self.value != rhs.value))
    def __len__(self) -> int:
        return self.size
    def __call__(self, value, kwarg):
        return self.get(String(value = "_call_"))(value)
    
    def append(self, val: Value) -> Value:
        self.value[Number(value = self.size)] = val
        self.size += 1
        return val
    def update(self, val: dict):
        self.value.update(val)
    def get(self, pos: Value):
        res = self.value.get(pos, Nil())
        if not isinstance(res, Nil):
            return res
        return super().get(pos)
    def set(self, pos: Value, val: Value):
        if self.value.get(pos) == None:
            raise RuntimeError(f"property {pos} didn't exist\nDid you mean := ?")
        self.value[pos] = val
    def define(self, pos: Value, val: Value):
        self.value[pos] = val
    def keys(self):
        res = Table()
        for k in self.value.keys():
            res.append(k)
        return res
    def values(self):
        res = Table()
        for k in self.value.keys():
            res.append(self.value[k])
        return res
    def pairs(self):
        res = Table()
        for k in self.value.keys():
            res.append(Table(value = {Number(value = 0): k, Number(value = 1): self.value[k]}, size = 2))
        return res
    def toList(self):
        res = []
        for k in self.value.keys():
            if isinstance(k, int):
                res.append(self.value.get(k))
        return res
    def toDict(self):
        res = {}
        for k in self.value.keys():
            if not isinstance(k, int):
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
        return sum(self.toList())
    def mean(self) -> float:
        return sum(self.toList()) / len(self.toList())
    def median(self) -> float:
        lis = self.toList()
        lis.sort()
        if len(lis) % 2 == 1:
            return lis[len(lis) // 2]
        else:
            return (lis[len(lis) // 2] + lis[len(lis) // 2 - 1]) / 2
    def stdev(self) -> float:
        avg = self.mean()
        arr = list(map(lambda x: (x - avg) ** 2,self.toList()))
        return math.sqrt(sum(arr) / len(arr))
    def describe(self):
        return {
            "sum": self.sum(),
            "mean": self.mean(),
            "median": self.median(),
            "stdev": self.stdev()
        }
    def sort(self) -> None:
        pass
    def has(self, key: Value) -> Number:
        if not isinstance(self.get(key), Nil):
            return Number(value = 1)
        else:
            return Number(value = 0)
    def lPair(self) -> "Table":
        l = self.toList()
        res = Table()
        for pos, i in enumerate(l):
            if i < len(l) - 1:
                res.append([i, l[pos + 1]])
        return res
    def _iter_(self):
        # Default iterative protocol
        cur = 0
        end = self.size
        def nxt():
            nonlocal cur
            if cur < end:
                cur += 1
                return cur - 1
            else:
                return Nil()
        return nxt

class Env(dict):
    def __init__(self, outer: Optional["Env"] = None):
        self.outer = outer
    
    def read(self, name):
        if self.get(name) != None:
            return self.get(name)
        else:
            if self.outer == None:
                raise RuntimeError(f"Can't find variable {name}\n")
            return self.outer.read(name)
    
    def write(self, name, val):
        if self.get(name, None) != None: self[name] = val
        else: return self.outer.write(name, val)
    
    def define(self, name, val):
        self.update({name: val})
@dataclass
class Closure:
    params: list[str] = field(default_factory = list)
    default: dict[str: Value] = field(default_factory = dict)
    implementation: list[AST] = field(default_factory = list)
    env: "Env" = field(default_factory = Env)
    isDynamic: bool = False

    def __init__(self, params, implementation, env, isDynamic):
        self.params = []
        self.default = {}
        for item in params:
            if isinstance(item, list):
                self.params.append(item[0])
                self.default[item[0]] = item[1]
            else:
                self.params.append(item)
        self.implementation = implementation; self.env = snapshot(env) if not isDynamic else env;
        self.isDynamic = isDynamic
        self.env.update({"this": self})

    def __eq__(self, rhs):
        if not isinstance(rhs, Closure): return False
        return self.params == rhs.params and self.implementation == rhs.implementation
    def __neq__(self, rhs):
        if not isinstance(rhs, Closure): return True
        return self.params != rhs.params or self.implementation != rhs.implementation

    def __call__(self, value, kwarg):
        nEnv = self.env
        nEnv.update(self.default)
        if len(value) > len(self.params):
            value = value[0:len(self.params)]
        nEnv.update(zip(self.params[0:len(value)], value))
        nEnv.update(kwarg)
        lst = None
        for ast in self.implementation:
            from teeny.interpreter import interpret
            lst = interpret(ast, nEnv)
        return lst

@dataclass
class Error(Value):
    typ: str = ""
    value: str = ""

    def __post_init__(self):
        self.register(String(value = "type"), String(value = self.typ))
        self.register(String(value = "value"), String(value = self.value))

@dataclass
class ValError(Value):
    typ: str = ""
    value: str = ""

    def __post_init__(self):
        self.register(String(value = "type"), String(value = self.typ))
        self.register(String(value = "value"), String(value = self.value))

@dataclass
class Nil(Value):
    pass

@dataclass
class BuiltinClosure(Value):
    fn: Callable = lambda: 0
    hasEnv: bool = False

    def __call__(self, value: list, kwarg: dict = {}):
        return self.fn(*value, **kwarg)

@dataclass
class BuiltinValue(Value):
    value: Value = field(default_factory = Nil)

@dataclass
class Underscore(Value):
    pass

def snapshot(e: Env):
    if e.outer == None:
        res = Env(None)
        res.update(e.copy())
        return res
    else:
        res = Env(snapshot(e.outer))
        res.update(e.copy())
        return res

def isTruthy(value: Value):
    if isinstance(value, Number):
        return bool(value.value)
    elif isinstance(value, Table):
        return len(value.value) > 0
    elif isinstance(value, Closure) or isinstance(value, BuiltinClosure):
        return True
    elif isinstance(value, Nil):
        return False
    elif isinstance(value, BuiltinValue):
        return isTruthy(value.value)

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

def makeObject(value: Value) -> list | dict | str | int | bool | None:
    if isinstance(value, Number): return value.value
    elif isinstance(value, String): return value.value
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
                res.update({makeObject(i): makeObject(value.value.get(i))})
            return res
    elif isinstance(value, Nil):
        return None
    elif isinstance(value, Closure):
        return "Closure"
def match(l: Value, r: Value) -> bool:
    if isinstance(l, Underscore):
        return True
    elif isinstance(l, Number): return isTruthy(l == r)
    elif isinstance(l, String): return isTruthy(l == r)
    elif isinstance(l, Table):
        if not isinstance(r, Table): return False
        for k in l.value.keys():
            if r.value.get(k) == None: return False
            if not match(l.get(k), r.get(k)): return False
        return True

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