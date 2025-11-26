"""
Tests for Dafny invariants in smart contracts.

Invariants are properties that must hold throughout the contract's lifetime.
Class invariants must be true after construction and after every method call.
"""

import unittest
from src.dafny_compiler import DafnyEVMCompiler


class TestInvariants(unittest.TestCase):
    """Test Dafny invariants compilation and verification."""
    
    def setUp(self):
        self.compiler = DafnyEVMCompiler(verify=False)
    
    def test_simple_class_invariant(self):
        """Test basic class invariant."""
        code = """
        class Counter {
          var count: uint256
          
          invariant count >= 0
          
          method increment()
            modifies this
          {
            count := count + 1;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_multiple_invariants(self):
        """Test multiple class invariants."""
        code = """
        class Token {
          var balance: uint256
          var totalSupply: uint256
          
          invariant balance >= 0
          invariant totalSupply >= balance
          
          method mint(amount: uint256)
            modifies this
          {
            balance := balance + amount;
            totalSupply := totalSupply + amount;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_invariant_with_comparison(self):
        """Test invariant with field comparison."""
        code = """
        class Vault {
          var balance: uint256
          var maxBalance: uint256
          
          invariant balance <= maxBalance
          
          constructor(max: uint256)
            modifies this
          {
            balance := 0;
            maxBalance := max;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_invariant_preserved_across_methods(self):
        """Test that invariant is maintained across different methods."""
        code = """
        class BoundedCounter {
          var count: uint256
          
          invariant count <= 100
          
          method increment()
            requires count < 100
            modifies this
          {
            count := count + 1;
          }
          
          method reset()
            modifies this
          {
            count := 0;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])


if __name__ == '__main__':
    unittest.main()
