import unittest
from teeny.runner import run_code
from teeny.value import makeObject, Error, Nil

class TestString(unittest.TestCase):
    def test_string_operator(self):
        self.assertEqual(makeObject(run_code('"a" == "a"', False, False, False)), 1)
        self.assertEqual(makeObject(run_code('"a" != "b"', False, False, False)), 1)
        self.assertEqual(makeObject(run_code('"a" < "b"', False, False, False)), 1)
        self.assertEqual(makeObject(run_code('"a" <= "b"', False, False, False)), 1)
        self.assertEqual(makeObject(run_code('"a" > "b"', False, False, False)), 0)
        self.assertEqual(makeObject(run_code('"a" >= "b"', False, False, False)), 0)
        self.assertEqual(makeObject(run_code('"a" + "b"', False, False, False)), "ab")
        self.assertEqual(makeObject(run_code('"a" * 3', False, False, False)), "aaa")
    def test_string_get_and_set(self):
        self.assertEqual(makeObject(run_code('"a"[0]', False, False, False)), "a")
        self.assertEqual(makeObject(run_code('a := "a"; a[0] = "b"; a', False, False, False)), "b")
        self.assertEqual(run_code('"a"["b"] = "b"', False, False, False), Error(typ = "Runtime Error", value = "index string with non-Number"))
    def test_string_builtin(self):
        self.assertEqual(makeObject(run_code('"a".len()', False, False, False)), 1)
        self.assertEqual(makeObject(run_code('"abcde".slice(1, 3)', False, False, False)), "bcd")
        self.assertEqual(makeObject(run_code('"abcde".find("bcd")', False, False, False)), 1)
        self.assertEqual(makeObject(run_code('"AbCdE".upper()', False, False, False)), "ABCDE")
        self.assertEqual(makeObject(run_code('"AbCdE".lower()', False, False, False)), "abcde")
        self.assertEqual(makeObject(run_code('"AbCdE".cap()', False, False, False)), "Abcde")
        self.assertEqual(makeObject(run_code('"  abc   ".trim()', False, False, False)), "abc")
        self.assertEqual(makeObject(run_code('"a b c".split(" ")', False, False, False)), ["a", "b", "c"])
        self.assertEqual(makeObject(run_code('" ".join(["a", "b", "c"])', False, False, False)), "a b c")
    def test_string_interpolation(self):
        self.assertEqual(makeObject(run_code('name := 1; "a{name}b"', False, False, False)), "a1b")
        self.assertEqual(makeObject(run_code('name := 1; "a\{name\}b"', False, False, False)), "a{name}b")
        self.assertEqual(makeObject(run_code('name := 1; "a{\'name\'}b"', False, False, False)), "anameb")
        self.assertEqual(makeObject(run_code('name := 1; "a{\'{name}\'}b"', False, False, False)), "a1b")

if __name__ == "__main__":
    unittest.main()