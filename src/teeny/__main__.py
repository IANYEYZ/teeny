#!/usr/bin/env python3
import sys
from teeny.lexer import tokenize
from teeny.parser import parse
from teeny.processor import process
from teeny.interpreter import interpret
from teeny.exception import LexicalError, SyntaxError, RuntimeError
from teeny.value import makeObject
from teeny.runner import run_code


def main():
    if len(sys.argv) < 2:
        while True:
            src = input("teeny> ")
            if src == ":exit":
                break
            run_code(src, is_file = False)
        sys.exit(0)
    run_code(sys.argv[1], print_each = True, print_res = False)

if __name__ == "__main__":
    main()
