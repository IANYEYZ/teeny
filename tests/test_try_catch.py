import unittest
from teeny.runner import run_code
from teeny.value import makeObject, Error, Nil

class TestTryCatch(unittest.TestCase):
    def test_try_catch(self):
        self.assertEqual(run_code('try e = 1 catch (e) => e.type', False, False, False), "Runtime Error")
        self.assertEqual(run_code('try test = 1 catch 1', False, False, False), Error(typ = 'Runtime Error', value = 'uncallable catch expression'))
        self.assertEqual(makeObject(run_code('try a := 1 catch (e) => e.type', False, False, False)), 1)

if __name__ == "__main__":
    unittest.main()