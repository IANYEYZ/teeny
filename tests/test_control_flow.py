import unittest
from teeny.runner import run_code
from teeny.value import makeObject, Error, Nil
from teeny.exception import SyntaxError

class TestControlFlow(unittest.TestCase):
    def test_block(self):
        self.assertEqual(makeObject(run_code('{1 + 2}', False, False, False)), 3)
        self.assertEqual(makeObject(run_code('{1 + 1; 1 + 2}', False, False, False)), 3)
        self.assertEqual(makeObject(run_code('a := 1; {a := 2}; a', False, False, False)), 1)
    def test_if(self):
        self.assertEqual(makeObject(run_code('a := 1; if a { 1 } else { 2 }', False, False, False)), 1)
        self.assertEqual(makeObject(run_code('a := 0; if a { 1 } else { 2 }', False, False, False)), 2)
        self.assertEqual(makeObject(run_code('a := 1; if a - 1 { 1 } elif a { 2 } else { 3 }', False, False, False)), 2)
        self.assertEqual(makeObject(run_code('a := 1; if a - 1 { 1 }', False, False, False)), None)
        self.assertEqual(makeObject(run_code('a := []; if a { 1 } else { 2 }', False, False, False)), 2)
        self.assertEqual(makeObject(run_code('a := [1]; if a { 1 } else { 2 }', False, False, False)), 1)
        self.assertEqual(makeObject(run_code('a := nil; if a { 1 } else { 2 }', False, False, False)), 2)
        self.assertEqual(makeObject(run_code('a := () => {}; if a { 1 } else { 2 }', False, False, False)), 1)
    def test_while(self):
        self.assertEqual(makeObject(run_code('a := 2; while a { a = a - 1; a - 1 }', False, False, False)), -1)
    def test_for(self):
        self.assertEqual(makeObject(run_code('for i in 1 .. 3 { i * i }', False, False, False)), [1, 4, 9])
        self.assertEqual(makeObject(run_code('for _ in 3.times() { 1 }', False, False, False)), [1, 1, 1])
        self.assertEqual(run_code('for i in 1 { i }', False, False, False), Error(typ = "Runtime Error", value = "iterate non-Table"))
    def test_match(self):
        self.assertEqual(makeObject(run_code('a := 3; match a { 1: 1, 2 : 2, _: 3 }', False, False, False)), 3)
        self.assertEqual(makeObject(run_code('isEven := (a) => a % 2; a := 3; match a { 1: 1, isEven: 2 }', False, False, False)), 2)
        self.assertEqual(makeObject(run_code('a := 3; match a { 1: 1 }', False, False, False)), None)
        self.assertEqual(makeObject(run_code('a := 15; match [a % 3, a % 5] { [1, 1]: 1, [0, _]: 2, _: 3 }', False, False, False)), 2)
        self.assertEqual(makeObject(run_code('a := "a"; match a { "a": 1, _: 3 }', False, False, False)), 1)

if __name__ == "__main__":
    unittest.main()