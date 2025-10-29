#!/usr/bin/env python3
import sys
from teeny.lexer import tokenize
from teeny.parser import parse
from teeny.processor import process
from teeny.interpreter import interpret
from teeny.exception import LexicalError, SyntaxError, RuntimeError
from teeny.value import makeObject

def run_file(path: str, print_each: bool = True):
    try:
        src = open(path, "r", encoding="utf-8").read()
        tokens = tokenize(src)
        pos = 0
        last_result = None

        while pos < len(tokens):
            before = pos
            ast, pos = parse(tokens, pos)  # must advance

            if pos == before:
                # Defensive: avoid infinite loop on bad parser progress
                raise SyntaxError(f"Parser made no progress at token index {pos}")

            value = interpret(process(ast))
            last_result = value
            if print_each and value is not None:
                print(makeObject(value))

        # If you prefer “print only the last value”, set print_each=False
        # and print here instead:
        if not print_each and last_result is not None:
            print(makeObject(last_result))

    except FileNotFoundError:
        print(f"File not found: {path}")
    except (LexicalError, SyntaxError, RuntimeError) as e:
        print(e)

def main():
    if len(sys.argv) < 2:
        print("Usage: teeny <file.ty>")
        sys.exit(1)
    run_file(sys.argv[1], print_each=True)

if __name__ == "__main__":
    main()
