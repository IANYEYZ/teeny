from teeny.AST import AST
def process(ast: AST) -> AST:
    for pos, c in enumerate(ast.children):
        ast.children[pos] = process(c)
    return ast