import unittest
from teeny.runner import run_code
from teeny.value import makeObject, Error, Nil
from teeny.AST import AST, toString

class TestAST(unittest.TestCase):
    def test_ast_to_string(self):
        self.assertEqual(AST('NUMBER', [], '1').toString(), 'NUMBER 1\n')
        self.assertEqual(AST('OP', [AST('NUMBER', [], '1'), AST('NUMBER', [], '2')], '+').toString(), 'OP +\n    NUMBER 1\n    NUMBER 2\n')
    def test_ast_repr(self):
        self.assertEqual(AST('NUMBER', [], '1').__repr__(), 'NUMBER 1\n')
        self.assertEqual(AST('OP', [AST('NUMBER', [], '1'), AST('NUMBER', [], '2')], '+').__repr__(), 'OP +\n    NUMBER 1\n    NUMBER 2\n')
    def test_list_to_string(self):
        self.assertEqual(toString([1, 2, 3]), '[1, 2, 3]')

if __name__ == "__main__":
    unittest.main()