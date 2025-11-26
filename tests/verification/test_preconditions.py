"""
Tests for Dafny preconditions (requires clauses) in smart contracts.

Preconditions specify what must be true before a method executes.
They are enforced at runtime via require() statements in EVM.
"""

import unittest
from src.dafny_compiler import DafnyEVMCompiler


class TestPreconditions(unittest.TestCase):
    """Test Dafny preconditions compilation and enforcement."""
    
    def setUp(self):
        self.compiler = DafnyEVMCompiler(verify=False)
    
    def test_simple_precondition(self):
        """Test basic precondition with comparison."""
        code = """
        class Counter {
          var count: uint256
          
          method increment()
            requires count < 100
            modifies this
          {
            count := count + 1;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
        
        # Check Yul contains precondition check
        yul = result.get('yul_code', '')
        self.assertIn("if iszero", yul)
        self.assertIn("revert", yul)
    
    def test_multiple_preconditions(self):
        """Test method with multiple preconditions."""
        code = """
        class Token {
          var balance: uint256
          
          method transfer(amount: uint256)
            requires amount > 0
            requires amount <= balance
            modifies this
          {
            balance := balance - amount;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
        
        # Both preconditions should generate checks
        yul = result.get('yul_code', '')
        self.assertGreaterEqual(yul.count("if iszero"), 2)
    
    def test_precondition_with_global_variable(self):
        """Test precondition using msg.sender."""
        code = """
        class Owned {
          var owner: address
          
          method setOwner(newOwner: address)
            requires msg.sender == owner
            modifies this
          {
            owner := newOwner;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
        
        # Should generate check for msg.sender
        yul = result.get('yul_code', '')
        self.assertIn("caller()", yul)
    
    def test_constructor_precondition(self):
        """Test precondition in constructor."""
        code = """
        class Token {
          var totalSupply: uint256
          
          constructor(initialSupply: uint256)
            requires initialSupply > 0
            modifies this
          {
            totalSupply := initialSupply;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])


if __name__ == '__main__':
    unittest.main()
