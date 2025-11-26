"""
Tests for Solidity-style custom modifiers.

Modifiers are reusable code that can be applied to methods.
Common examples: onlyOwner, whenNotPaused, nonReentrant.
"""

import unittest
from src.dafny_compiler import DafnyEVMCompiler


class TestModifiers(unittest.TestCase):
    """Test custom modifier declarations and usage."""
    
    def setUp(self):
        self.compiler = DafnyEVMCompiler(verify=False)
    
    def test_simple_modifier(self):
        """Test basic modifier declaration."""
        code = """
        class Owned {
          var owner: address
          
          modifier onlyOwner {
            require msg.sender == owner;
            _;
          }
          
          method setOwner(newOwner: address) onlyOwner
            modifies this
          {
            owner := newOwner;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_modifier_with_parameter(self):
        """Test modifier with parameters."""
        code = """
        class Token {
          var balance: uint256
          
          modifier onlyAbove(amount: uint256) {
            require balance >= amount;
            _;
          }
          
          method withdraw(amount: uint256) onlyAbove(amount)
            modifies this
          {
            balance := balance - amount;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_multiple_modifiers(self):
        """Test method with multiple modifiers."""
        code = """
        class Contract {
          var owner: address
          var paused: bool
          
          modifier onlyOwner {
            require msg.sender == owner;
            _;
          }
          
          modifier whenNotPaused {
            require paused == false;
            _;
          }
          
          method execute() onlyOwner whenNotPaused
            modifies this
          {
            // Do something
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])


if __name__ == '__main__':
    unittest.main()
