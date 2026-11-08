"""Software-only arithmetic guards; case numbers are unit-test inputs, not study data."""
import sys,unittest
from fractions import Fraction
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from retention_bounds import bound_full_reference_recall as b

class TestConditionalRecallBounds(unittest.TestCase):
    def test_fully_checked_reference(self):
        a=b(20,0,0)
        self.assertEqual((a.lower,a.upper),(Fraction(1),Fraction(1)))
    def test_unresolved_exclusions(self):
        a=b(20,0,10)
        self.assertEqual((a.lower,a.upper),(Fraction(2,3),Fraction(1)))
    def test_verified_misses(self):
        a=b(20,2,10)
        self.assertEqual((a.lower,a.upper),(Fraction(5,8),Fraction(10,11)))
    def test_no_known_retained(self):
        a=b(0,4,10)
        self.assertEqual((a.lower,a.upper),(Fraction(0),Fraction(0)))
    def test_lower_nonincreasing_as_unresolved_grows(self):
        self.assertGreater(b(30,2,5).lower,b(30,2,6).lower)
        self.assertEqual(b(30,2,5).upper,b(30,2,6).upper)
    def test_no_eligible_reference_is_unidentified(self):
        with self.assertRaises(ValueError):b(0,0,10)
    def test_negative_and_bool_rejected(self):
        for vals in ((-1,2,3),(1,2,-3),(1,False,3),(1,2,3.0)):
            with self.subTest(vals=vals), self.assertRaises(ValueError):b(*vals)
    def test_integer_bounds_do_not_treat_unknown_as_observed_miss(self):
        a=b(8,2,3)
        for z in range(4):
            val=Fraction(8,10+z)
            self.assertLessEqual(a.lower,val)
            self.assertLessEqual(val,a.upper)

if __name__=='__main__': unittest.main()
