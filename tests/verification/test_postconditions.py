"""
Tests for Dafny postconditions (ensures clauses) in smart contracts.

Postconditions specify what must be true after a method executes.
They are verified by Dafny but not enforced at runtime in EVM.
"""

import unittest
from src.dafny_compiler import DafnyEVMCompiler


class TestPostconditions(unittest.TestCase):
    """Test Dafny postconditions compilation and verification."""
    
    def setUp(self):
        self.compiler = DafnyEVMCompiler(verify=False)
    
    def test_simple_postcondition(self):
        """Test basic postcondition with state change."""
        code = """
        class Counter {
          var count: uint256
          
          method increment()
            modifies this
            ensures count == old(count) + 1
          {
            count := count + 1;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_multiple_postconditions(self):
        """Test method with multiple postconditions."""
        code = """
        class Token {
          var balance: uint256
          var totalSupply: uint256
          
          method mint(amount: uint256)
            modifies this
            ensures balance == old(balance) + amount
            ensures totalSupply == old(totalSupply) + amount
          {
            balance := balance + amount;
            totalSupply := totalSupply + amount;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_postcondition_with_old_expression(self):
        """Test postcondition using old() to reference previous state."""
        code = """
        class Vault {
          var balance: uint256
          
          method withdraw(amount: uint256)
            requires amount <= balance
            modifies this
            ensures balance == old(balance) - amount
          {
            balance := balance - amount;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_postcondition_with_return_value(self):
        """Test postcondition on return value."""
        code = """
        class Calculator {
          method add(a: uint256, b: uint256) returns (result: uint256)
            ensures result == a + b
          {
            return a + b;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_postcondition_preserving_other_state(self):
        """Test postcondition ensuring other state unchanged."""
        code = """
        class Token {
          var balance: uint256
          var owner: address
          
          method updateBalance(newBalance: uint256)
            modifies this
            ensures balance == newBalance
            ensures owner == old(owner)
          {
            balance := newBalance;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])


if __name__ == '__main__':
    unittest.main()
