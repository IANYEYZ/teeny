from teeny.lexer import tokenize
from teeny.parser import parse
from teeny.processor import process
from teeny.interpreter import interpret
from teeny.exception import LexicalError, SyntaxError, RuntimeError
from teeny.value import makeObject

def readFromExample(name):
    return open(f"../example/{name}.ty").read()

rhs = None; p = 0
while True:
    try:
        rhs, p = parse(tokenize(readFromExample("expr")), p)
        # print(process(rhs))
        print(makeObject(interpret(process(rhs))))
    except LexicalError as e:
        print(e)
        break
    except SyntaxError as e:
        print(e)
        break
    except RuntimeError as e:
        print(e)
        break
    # print(rhs)
    if p >= len(tokenize(readFromExample("expr"))):
        break