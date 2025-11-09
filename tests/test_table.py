import unittest
from teeny.runner import run_code
from teeny.value import makeObject, Error, Nil

class TestTable(unittest.TestCase):
    def test_table_create(self):
        self.assertEqual(makeObject(run_code('[1, 2, 3]', False, False, False)), [1, 2, 3])
        self.assertEqual(makeObject(run_code('[a: 1, b: 2]', False, False, False)), {'a': 1, 'b' : 2})
        self.assertEqual(makeObject(run_code('[a: 1, "b": 2, 3]', False, False, False)), {'a': 1, 'b' : 2, '0': 3})
    def test_table_get_and_set(self):
        self.assertEqual(makeObject(run_code('a := [1, 2, 3]; a[0]', False, False, False)), 1)
        self.assertEqual(makeObject(run_code('a := [a: 1, b: 2]; a.b', False, False, False)), 2)
        self.assertEqual(makeObject(run_code('a := [1, 2, 3]; a[0] = 2; a', False, False, False)), [2, 2, 3])
        self.assertEqual(makeObject(run_code('a := [a: 1, b: 2]; a.b = 3; a', False, False, False)), {'a': 1, 'b': 3})
        self.assertEqual(makeObject(run_code('a := []; [a[0], a[1]] := [2, 3]', False, False, False)), [2, 3])
        self.assertEqual(makeObject(run_code('a := []; [a.b, a.a] := [3, 4]; a', False, False, False)), {'a': 4, 'b': 3})
        self.assertEqual(makeObject(run_code('a := [1, nil]; [a[0], a[1]] ?= [2, 3]', False, False, False)), [1, 3])
        self.assertEqual(makeObject(run_code('a := [a: nil, b: 1]; [a.b, a.a] ?= [3, 4]; a', False, False, False)), {'a': 4, 'b': 1})
    def test_table_operator(self):
        self.assertEqual(makeObject(run_code('[1, 2, 3] + [4, 5, 6]', False, False, False)), [1, 2, 3, 4, 5, 6])
        self.assertEqual(makeObject(run_code('[a: 1] + [b: 2]', False, False, False)), {'a': 1, 'b': 2})
        self.assertEqual(makeObject(run_code('[a: 1] == [b: 2]', False, False, False)), 0)
        self.assertEqual(makeObject(run_code('[a: 1] != [b: 2]', False, False, False)), 1)
    def test_table_builtin(self):
        self.assertEqual(makeObject(run_code('[1, 2, 3].keys()', False, False, False)), [0, 1, 2])
        self.assertEqual(makeObject(run_code('[a: 1, b: 2].values()', False, False, False)), [1, 2])
        self.assertEqual(makeObject(run_code('[a: 1, b: 2].pairs()', False, False, False)), [["a", 1], ["b", 2]])
        self.assertEqual(makeObject(run_code('[1, 2, 3].map((x) => x * x)', False, False, False)), [1, 4, 9])
        self.assertEqual(makeObject(run_code('[1, 2, 3].filter((x) => x % 2)', False, False, False)), [1, 3])
        self.assertEqual(makeObject(run_code('[a: 1].filter((x) => x % 2)', False, False, False)), {"a": 1})
        self.assertEqual(makeObject(run_code('[1, 2, 3].sum()', False, False, False)), 6)
        self.assertEqual(makeObject(run_code('[1, 2, 3].mean()', False, False, False)), 2)
        self.assertEqual(makeObject(run_code('[1, 2, 3].median()', False, False, False)), 2)
        self.assertEqual(makeObject(run_code('[1, 2, 3, 4].median()', False, False, False)), 2.5)
        self.assertEqual(makeObject(run_code('[1, 3, 2].sort()', False, False, False)), [1, 2, 3])
        self.assertAlmostEqual(makeObject(run_code('[1, 2, 3].stdev()', False, False, False)), 0.816496580927726)
        self.assertEqual(makeObject(run_code('[1, 2, 3].describe()', False, False, False)), {
            "sum": 6,
            "mean": 2.0,
            "median": 2,
            "stdev": 0.816496580927726
        })

if __name__ == "__main__":
    unittest.main()