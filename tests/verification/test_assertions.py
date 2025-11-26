"""
Tests for Dafny assert statements in smart contracts.

Assert statements check conditions during execution and help verify correctness.
They are compiled to EVM revert if the condition is false.
"""

import unittest
from src.dafny_compiler import DafnyEVMCompiler


class TestAssertions(unittest.TestCase):
    """Test Dafny assert statements compilation."""
    
    def setUp(self):
        self.compiler = DafnyEVMCompiler(verify=False)
    
    def test_simple_assert(self):
        """Test basic assert statement."""
        code = """
        class Calculator {
          method checkPositive(x: uint256)
          {
            assert x >= 0;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_assert_with_arithmetic(self):
        """Test assert with arithmetic expression."""
        code = """
        class Math {
          method doubleCheck(x: uint256) returns (result: uint256)
          {
            result := x * 2;
            assert result >= x;
            return result;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_assert_with_state(self):
        """Test assert checking state variable."""
        code = """
        class Counter {
          var count: uint256
          
          method increment()
            modifies this
          {
            var oldCount: uint256 := count;
            count := count + 1;
            assert count == oldCount + 1;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_multiple_asserts(self):
        """Test multiple assert statements in sequence."""
        code = """
        class Validator {
          method validate(x: uint256, y: uint256)
          {
            assert x >= 0;
            assert y >= 0;
            assert x + y >= x;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])


if __name__ == '__main__':
    unittest.main()
