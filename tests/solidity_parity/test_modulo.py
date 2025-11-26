"""
Tests for modulo operator (%).
"""

import unittest
from src.dafny_compiler import DafnyEVMCompiler


class TestModuloOperator(unittest.TestCase):
    """Test modulo operator support."""
    
    def setUp(self):
        self.compiler = DafnyEVMCompiler(verify=False)
    
    def test_modulo_basic(self):
        """Test basic modulo operation."""
        code = """
        class Contract {
          method modulo(a: uint256, b: uint256) pure returns (x: uint256) {
            return a % b;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_modulo_in_expression(self):
        """Test modulo in complex expression."""
        code = """
        class Contract {
          method calculate(a: uint256, b: uint256) pure returns (x: uint256) {
            return (a + b) % 10;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_modulo_assignment(self):
        """Test modulo with assignment."""
        code = """
        class Contract {
          var value: uint256
          
          method updateMod(a: uint256, b: uint256)
            modifies this
          {
            value := a % b;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_modulo_with_literals(self):
        """Test modulo with literal values."""
        code = """
        class Contract {
          method isEven(n: uint256) pure returns (x: bool) {
            return n % 2 == 0;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])


if __name__ == '__main__':
    unittest.main()
