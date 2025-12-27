import unittest
from teeny.runner import run_code
from teeny.value import makeObject, Error, Nil

class TestClosure(unittest.TestCase):
    def test_closure(self):
        self.assertEqual(makeObject(run_code('sum := fn (a, b) a + b; sum(1, 2)', False, False, False)), 3)
        self.assertEqual(makeObject(run_code('sum := (a, b) => a + b; sum(1, 2)', False, False, False)), 3)
        self.assertEqual(makeObject(run_code('sum := (a, b = 1) => a + b; sum(1)', False, False, False)), 2)
        self.assertEqual(makeObject(run_code('sum := (a, b) => a + b; sum(a = 2, b = 1)', False, False, False)), 3)
        self.assertEqual(makeObject(run_code('a := 1; f := () => a = a + 1; f(); a', False, False, False)), 2)
        self.assertEqual(makeObject(run_code('f1 := (a) => a + 1; f2 := (a) => a + 1; f1 == f2', False, False, False)), 0)
        self.assertEqual(makeObject(run_code('f1 := (a) => a + 1; f2 := (a) => a; f1 == f1', False, False, False)), 1)
        self.assertEqual(makeObject(run_code('f1 := (a) => a + 1; f2 := (a) => a; f1 != f1', False, False, False)), 0)
    def test_pipe(self):
        self.assertEqual(makeObject(run_code('sum := fn (a, b) a + b; 1 |> sum(2)', False, False, False)), 3)
        self.assertEqual(makeObject(run_code('f := fn (a, b) a + 2 * b; 1 |> f(2)', False, False, False)), 5)
        self.assertEqual(makeObject(run_code('f := fn (a, b) a + 2 * b; 1 |> f(2, _)', False, False, False)), 4)
    def test_dynamic_closure(self):
        self.assertEqual(makeObject(run_code('a := 1; f := () @=> a = a + 1; f(); a', False, False, False)), 1)
        self.assertEqual(makeObject(run_code('a := 1; f := (c) @=> a = c + 1; f(1); a', False, False, False)), 1)
        self.assertEqual(makeObject(run_code('a := 1; f := fn@ (c = 1) a = a + 1; f(); a', False, False, False)), 1)

if __name__ == "__main__":
    unittest.main()