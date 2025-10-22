from dataclasses import dataclass, field
from typing import Optional, Callable
from teeny.AST import AST
from teeny.exception import RuntimeError

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
        if not isinstance(rhs, Number): return Number(0)
        return Number(value = int(self.value == rhs.value))
    def __neq__(self, rhs) -> "Number":
        if not isinstance(rhs, Number): return Number(1)
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

@dataclass
class String(Value):
    value: str = ""

    def __add__(self, rhs) -> "String":
        return String(value = self.value + rhs.value)
    def __eq__(self, rhs) -> Number:
        if not isinstance(rhs, String): return Number(0)
        return Number(value = self.value == rhs.value)
    def __neq__(self, rhs) -> Number:
        if not isinstance(rhs, String): return Number(1)
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

@dataclass
class Table(Value):
    value: dict[Value: Value] = field(default_factory=dict)
    size: int = 0

    def __post_init__(self):
        self.register(String(value = "push"), BuiltinClosure(fn = self.append))
        self.register(String(value = "keys"), BuiltinClosure(fn = self.keys))
        self.register(String(value = "values"), BuiltinClosure(fn = self.values))
        self.register(String(value = "pairs"), BuiltinClosure(fn = self.pairs))
        self.register(String(value = "_iter_"), BuiltinClosure(fn = self._iter_))

    def __add__(self, rhs: "Table") -> "Table":
        return Table(value = {**self.value, **rhs.value})
    def __eq__(self, rhs) -> Number:
        if not isinstance(rhs, Table): return Number(0)
        return Number(value = int(self.value == rhs.value))
    def __neq__(self, rhs) -> Number:
        if not isinstance(rhs, Table): return Number(1)
        return Number(value = int(self.value != rhs.value))
    def __len__(self) -> int:
        return self.size
    def __call__(self, value):
        return self.get("_call_")(value)
    
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
        if self.get(name, None) != None:
            return self.get(name)
        else:
            if self.outer == None:
                raise RuntimeError(f"Can't find variable {name}, current env {self}\n")
            return self.outer.read(name)
    
    def write(self, name, val):
        if self.get(name, None) != None: self[name] = val
        else: return self.outer.write(name, val)
    
    def define(self, name, val):
        self.update({name: val})

@dataclass
class Closure:
    params: list[str] = field(default_factory = list)
    implementation: list[AST] = field(default_factory = list)
    env: "Env" = field(default_factory = Env)
    isDynamic: bool = False

    def __init__(self, params, implementation, env, isDynamic):
        self.params = params; self.implementation = implementation; self.env = snapshot(env) if not isDynamic else env;
        self.isDynamic = isDynamic
        self.env.update({"this": self})

    def __eq__(self, rhs):
        if not isinstance(rhs, Closure): return False
        return self.params == rhs.params and self.implementation == rhs.implementation
    def __neq__(self, rhs):
        if not isinstance(rhs, Closure): return True
        return self.params != rhs.params or self.implementation != rhs.implementation

    def __call__(self, value, insideCatch = False):
        nEnv = self.env
        nEnv.update(zip(self.params, value))
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

    def __call__(self, value):
        return self.fn(*value)

@dataclass
class BuiltinValue(Value):
    value: Value = field(default_factory = Nil)

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