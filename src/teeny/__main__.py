#!/usr/bin/env python3
import sys
from teeny.lexer import tokenize
from teeny.parser import parse
from teeny.processor import process
from teeny.interpreter import interpret
from teeny.exception import LexicalError, SyntaxError, RuntimeError
from teeny.value import makeObject, String, makeTable
from teeny.runner import run_code
from teeny.glob import makeGlobal, getType
from pathlib import Path
import time
import os
import shutil

def checkParenBalance(src):
    cnt = [0, 0, 0]
    flag = [0, 0]
    for p in range(len(src)):
        if src[p] == "(" and not flag[0] and not flag[1]:
            cnt[0] += 1
        if src[p] == ")" and not flag[0] and not flag[1]:
            cnt[0] -= 1
        if src[p] == "[" and not flag[0] and not flag[1]:
            cnt[1] += 1
        if src[p] == "]" and not flag[0] and not flag[1]:
            cnt[1] -= 1
        if src[p] == "{" and not flag[0] and not flag[1]:
            cnt[2] += 1
        if src[p] == "}" and not flag[0] and not flag[1]:
            cnt[2] -= 1
        if src[p] == '"': flag[0] = not flag[0]
        if src[p] == "'": flag[1] = not flag[1]
    return cnt[0] == 0 and cnt[1] == 0 and cnt[2] == 0

def readCode():
    src = input("\033[36mteeny>\033[0m ")
    while not checkParenBalance(src):
        src += input("\033[36m...>  \033[0m ")
    return src

C = {
    "cmd": "\033[36m",     # cyan
    "arg": "\033[33m",     # yellow
    "hdr": "\033[35;1m",   # bold magenta
    "desc": "\033[90m",
    "rst": "\033[0m"
}

helpText = f"""{C['hdr']}Teeny REPL commands:{C['rst']}
    {C['cmd']}:help{C['rst']}               {C['desc']}Show this message
    {C['cmd']}:exit{C['rst']}               {C['desc']}Exit the REPL

    {C['cmd']}:env{C['rst']}                {C['desc']}List all variables in the environment
    {C['cmd']}:reload{C['rst']}             {C['desc']}Reset to a fresh global environment
    {C['cmd']}:?{C['rst']} {C['arg']}<name>{C['rst']}           {C['desc']}Inspect a variable (type and value)

    {C['cmd']}:time{C['rst']} {C['arg']}<expr>{C['rst']}        {C['desc']}Evaluate <expr> and show execution time
    {C['cmd']}:ast{C['rst']}  {C['arg']}<expr>{C['rst']}        {C['desc']}Show parsed AST for <expr> (does not execute)"""

banner = """\033[35;1mTeeny\033[0m  —  Tiny Expression Language
Type \033[36m:help\033[0m for help."""

def main():
    if len(sys.argv) < 2:
        env = makeGlobal()
        print(banner)
        while True:
            src = readCode()
            if src == ":exit":
                break
            elif src == ":reload":
                env = makeGlobal()
                continue
            elif src == ":env":
                print(f"Environment({len(env.keys())} bindings)")
                for k in env.keys():
                    print(f"{k}: {getType(env[k]).value}")
                continue
            elif src == ":help":
                print(helpText)
                continue
            flag = False; st, ed = None, None
            if len(src) >= 5 and src[0:5] == ":time":
                flag = True
                src = src[5:].strip()
            onlyAST = False
            inspect = False
            if len(src) >= 4 and src[0:4] == ":ast":
                onlyAST = True
                src = src[4:].strip()
            if len(src) >= 2 and src[0:2] == ":?":
                inspect = True
                src = src[2:].strip()
            if flag: st = time.time()
            if not onlyAST and not inspect: run_code(src, is_file = False, print_each = False, defEnv = env)
            elif not inspect: print(parse(tokenize(src))[0])
            else: print(f"{src}: {getType(env.get(src)).value} = {makeObject(env.get(src))}")
            if flag:
                ed = time.time()
                print("Time: ", ed - st, "s")
        sys.exit(0)
    elif sys.argv[1] == "install":
        dir = sys.argv[2] if len(sys.argv) > 2 else "."
        if not Path(dir).is_dir():
            print("Error: Module didn't exists or is not a folder")
            sys.exit(1)
        # We try to move the package to ../../lib
        dest = Path(__file__).parent.parent.parent / "lib"
        src = Path(dir).resolve()
        shutil.copytree(src, dest / src.name, dirs_exist_ok = True)
        print(f"Module {src.name} installed successfully.")
        sys.exit(0)
        
    run_code(sys.argv[1], print_each = True, print_res = False)

if __name__ == "__main__":
    main()
