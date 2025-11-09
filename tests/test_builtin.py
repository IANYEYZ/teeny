import unittest
import math, random
from teeny.runner import run_code
from teeny.value import makeObject
import json


class TestBuiltin(unittest.TestCase):
    def test_math(self):
        # --- constants ---
        self.assertAlmostEqual(makeObject(run_code('math.pi', False, False, False)), math.pi)
        self.assertAlmostEqual(makeObject(run_code('math.e', False, False, False)), math.e)
        self.assertAlmostEqual(makeObject(run_code('math.tau', False, False, False)), math.tau)

        # --- basic operations ---
        self.assertEqual(makeObject(run_code('math.abs(-5)', False, False, False)), 5)
        self.assertEqual(makeObject(run_code('math.floor(3.7)', False, False, False)), 3)
        self.assertEqual(makeObject(run_code('math.ceil(3.2)', False, False, False)), 4)
        self.assertEqual(makeObject(run_code('math.trunc(3.9)', False, False, False)), 3)
        self.assertEqual(makeObject(run_code('math.round(3.5)', False, False, False)), round(3.5))

        # --- min/max/clamp/lerp ---
        self.assertEqual(makeObject(run_code('math.min(2, 5)', False, False, False)), 2)
        self.assertEqual(makeObject(run_code('math.max(2, 5)', False, False, False)), 5)
        self.assertEqual(makeObject(run_code('math.clamp(10, 0, 5)', False, False, False)), 5)
        self.assertEqual(makeObject(run_code('math.clamp(-1, 0, 5)', False, False, False)), 0)
        self.assertAlmostEqual(makeObject(run_code('math.lerp(0, 10, 0.3)', False, False, False)), 3.0)

        # --- sign ---
        self.assertEqual(makeObject(run_code('math.sign(-10)', False, False, False)), -1)
        self.assertEqual(makeObject(run_code('math.sign(10)', False, False, False)), 1)

        # --- trig functions ---
        self.assertAlmostEqual(makeObject(run_code('math.sin(math.pi / 2)', False, False, False)), 1.0)
        self.assertAlmostEqual(makeObject(run_code('math.cos(math.pi)', False, False, False)), -1.0)
        self.assertAlmostEqual(makeObject(run_code('math.tan(0)', False, False, False)), 0.0)

        self.assertAlmostEqual(makeObject(run_code('math.asin(1)', False, False, False)), math.asin(1))
        self.assertAlmostEqual(makeObject(run_code('math.acos(1)', False, False, False)), math.acos(1))
        self.assertAlmostEqual(makeObject(run_code('math.atan(1)', False, False, False)), math.atan(1))
        self.assertAlmostEqual(makeObject(run_code('math.atan2(1, 1)', False, False, False)), math.atan2(1, 1))

        # --- angle conversions ---
        self.assertAlmostEqual(makeObject(run_code('math.degrees(math.pi)', False, False, False)), 180)
        self.assertAlmostEqual(makeObject(run_code('math.radians(180)', False, False, False)), math.pi)

        # --- exponential / power / log ---
        self.assertAlmostEqual(makeObject(run_code('math.exp(1)', False, False, False)), math.e)
        self.assertAlmostEqual(makeObject(run_code('math.pow(2, 3)', False, False, False)), 8)
        self.assertAlmostEqual(makeObject(run_code('math.log(math.e)', False, False, False)), 1)
        self.assertAlmostEqual(makeObject(run_code('math.log(8, 2)', False, False, False)), 3)
        self.assertAlmostEqual(makeObject(run_code('math.log10(100)', False, False, False)), 2)
        self.assertAlmostEqual(makeObject(run_code('math.log2(8)', False, False, False)), 3)

        # --- hypot ---
        self.assertAlmostEqual(makeObject(run_code('math.hypot(3, 4)', False, False, False)), 5)

        # --- random related ---
        val = makeObject(run_code('math.random()', False, False, False))
        self.assertTrue(0 <= val <= 1)
        val2 = makeObject(run_code('math.uniform(2, 3)', False, False, False))
        self.assertTrue(2 <= val2 <= 3)
        val3 = makeObject(run_code('math.randint(1, 10)', False, False, False))
        self.assertTrue(1 <= val3 <= 10)

        # --- comparisons ---
        self.assertTrue(makeObject(run_code('math.eq(2, 2)', False, False, False)))
        self.assertFalse(makeObject(run_code('math.eq(2, 3)', False, False, False)))
        self.assertTrue(makeObject(run_code('math.lt(1, 2)', False, False, False)))
        self.assertTrue(makeObject(run_code('math.gt(3, 2)', False, False, False)))
        self.assertTrue(makeObject(run_code('math.le(2, 2)', False, False, False)))
        self.assertTrue(makeObject(run_code('math.ge(2, 2)', False, False, False)))
        self.assertTrue(makeObject(run_code('math.neq(1, 2)', False, False, False)))
    
    def test_json(self):
        # --- encode basic types ---
        self.assertEqual(makeObject(run_code('json.encode(123)', False, False, False)), json.dumps(123))
        self.assertEqual(makeObject(run_code('json.encode("hi")', False, False, False)), json.dumps("hi"))
        self.assertEqual(makeObject(run_code('json.encode(nil)', False, False, False)), json.dumps(None))

        # --- stringnify alias ---
        self.assertEqual(makeObject(run_code('json.stringnify(42)', False, False, False)), json.dumps(42))

        # --- encode table/object ---
        code = 'json.encode([ "a": 1, "b": 2 ])'
        self.assertEqual(makeObject(run_code(code, False, False, False)), json.dumps({"a": 1, "b": 2}))

        # --- decode basic types ---
        self.assertEqual(makeObject(run_code('json.decode("123")', False, False, False)), 123)
        self.assertEqual(makeObject(run_code('json.decode("true")', False, False, False)), True)
        self.assertIsNone(makeObject(run_code('json.decode("null")', False, False, False)))

        # --- parse alias ---
        self.assertEqual(makeObject(run_code('json.parse("123")', False, False, False)), 123)

        # --- roundtrip consistency ---
        roundtrip = makeObject(run_code('json.decode(json.encode([ "x": 5, "y": [1,2,3] ]))', False, False, False))
        self.assertEqual(roundtrip, {"x": 5, "y": [1, 2, 3]})


if __name__ == "__main__":
    unittest.main()
