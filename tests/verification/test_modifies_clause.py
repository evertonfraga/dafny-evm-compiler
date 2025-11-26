"""
Tests for Dafny modifies clauses in smart contracts.

The modifies clause specifies which objects a method may modify.
This is essential for frame conditions and verification.
"""

import unittest
from src.dafny_compiler import DafnyEVMCompiler


class TestModifiesClause(unittest.TestCase):
    """Test Dafny modifies clauses compilation."""
    
    def setUp(self):
        self.compiler = DafnyEVMCompiler(verify=False)
    
    def test_modifies_this(self):
        """Test method that modifies this."""
        code = """
        class Counter {
          var count: uint256
          
          method increment()
            modifies this
          {
            count := count + 1;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_pure_method_no_modifies(self):
        """Test pure method without modifies clause."""
        code = """
        class Calculator {
          method add(a: uint256, b: uint256) returns (result: uint256)
          {
            return a + b;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_view_method_reads_state(self):
        """Test method that reads but doesn't modify state."""
        code = """
        class Token {
          var balance: uint256
          
          method getBalance() returns (b: uint256)
          {
            return balance;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_constructor_modifies_this(self):
        """Test constructor with modifies this."""
        code = """
        class Token {
          var totalSupply: uint256
          
          constructor(supply: uint256)
            modifies this
          {
            totalSupply := supply;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])


if __name__ == '__main__':
    unittest.main()
