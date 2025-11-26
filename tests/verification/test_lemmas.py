"""
Tests for Dafny lemmas in smart contracts.

Lemmas are ghost methods that prove mathematical properties.
They help verify complex invariants and postconditions.
"""

import unittest
from src.dafny_compiler import DafnyEVMCompiler


class TestLemmas(unittest.TestCase):
    """Test Dafny lemmas for proofs."""
    
    def setUp(self):
        self.compiler = DafnyEVMCompiler(verify=False)
    
    def test_simple_lemma(self):
        """Test basic lemma proving a property."""
        code = """
        class Math {
          lemma AdditionCommutative(a: int, b: int)
            ensures a + b == b + a
          {
          }
          
          method add(x: uint256, y: uint256) returns (result: uint256)
          {
            return x + y;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_lemma_with_requires(self):
        """Test lemma with preconditions."""
        code = """
        class Token {
          var balance: uint256
          
          lemma BalanceNonNegative()
            requires balance >= 0
            ensures balance >= 0
          {
          }
          
          method getBalance() returns (b: uint256)
          {
            return balance;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_lemma_for_invariant(self):
        """Test lemma helping prove an invariant."""
        code = """
        class Counter {
          var count: uint256
          
          invariant count >= 0
          
          lemma CountAlwaysNonNegative()
            ensures count >= 0
          {
          }
          
          method increment()
            modifies this
          {
            count := count + 1;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])


if __name__ == '__main__':
    unittest.main()
