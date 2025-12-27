from teeny.value import Env
from teeny.lexer import tokenize
from teeny.parser import parse
from teeny.processor import process
from teeny.interpreter import interpret
from teeny.exception import LexicalError, SyntaxError, RuntimeError
from teeny.value import makeObject, Error
from teeny.glob import makeGlobal

def run(code: str, env: Env = makeGlobal()) -> Env:
    rhs = None; p = 0
    while True:
        rhs, p = parse(tokenize(code), p)
        interpret(process(rhs), env)
        if p >= len(tokenize(code)):
            break
    return env

def run_code(pathOrCode: str, print_each: bool = True, print_res: bool = True, is_file: bool = True, defEnv: Env = makeGlobal()) -> None:
    env = defEnv
    try:
        src = None
        if is_file: src = open(pathOrCode, "r", encoding="utf-8").read()
        else: src = pathOrCode
        tokens = tokenize(src)
        pos = 0
        last_result = None
        results = []
        while pos < len(tokens):
            before = pos
            ast, pos = parse(tokens, pos)
            if pos == before:
                raise SyntaxError(f"Parser made no progress at token index {pos}")
            value = None
            try:
                value = interpret(process(ast), env)
            except RecursionError as e:
                print(e)
            last_result = value
            if isinstance(value, Error):
                if print_res: print("=>", makeObject(value))
                # print(ast)
                print(makeObject(value))
                return value
            if print_each and value is not None:
                if print_res: print("=>", makeObject(value))
                results.append(value)
        if not print_each and last_result is not None:
            if print_res: print("=>", makeObject(last_result))
            return last_result
        if print_each: return results
        else: return None
    except FileNotFoundError:
        print(f"File not found: {pathOrCode}")
    except (LexicalError, SyntaxError, RuntimeError) as e:
        print(e)