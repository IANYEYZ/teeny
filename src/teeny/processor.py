from teeny.AST import AST
def process(ast: AST) -> AST:
    if ast == None:
        return
    newChildren = []
    for pos, c in enumerate(ast.children):
        if c != None:
            newChildren.append(process(c))
    ast.children = newChildren
    return ast