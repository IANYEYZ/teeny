from teeny.value import Env
from teeny.lexer import tokenize
from teeny.parser import parse
from teeny.processor import process
from teeny.interpreter import interpret
from teeny.glob import makeGlobal

def run(code: str, env: Env = makeGlobal()):
    rhs = None; p = 0
    while True:
        rhs, p = parse(tokenize(code), p)
        # print(process(rhs))
        interpret(process(rhs), env)
        # print(rhs)
        if p >= len(tokenize(code)):
            break
    return env