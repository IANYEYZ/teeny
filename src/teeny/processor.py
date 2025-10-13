from teeny.AST import AST
def process(ast: AST) -> AST:
    for pos, c in enumerate(ast.children):
        ast.children[pos] = process(c)
    if ast.value == "=" and ast.children[0].value == ".":
        newTree = AST("OP", [*ast.children[0].children, *ast.children[1:]], ".=")
        return newTree
    elif ast.value == ":=" and ast.children[0].value == ".":
        newTree = AST("OP", [*ast.children[0].children, *ast.children[1:]], ".:=")
        return newTree
    if ast.value == "=" and ast.children[0].value == "[]":
        newTree = AST("OP", [*ast.children[0].children, *ast.children[1:]], "[]=")
        return newTree
    elif ast.value == ":=" and ast.children[0].value == "[]":
        newTree = AST("OP", [*ast.children[0].children, *ast.children[1:]], "[]:=")
        return newTree
    return ast