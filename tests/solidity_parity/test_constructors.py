"""
Tests for Solidity-compatible constructors.

Constructors initialize contract state and run once during deployment.
"""

import unittest
from src.dafny_compiler import DafnyEVMCompiler


class TestConstructors(unittest.TestCase):
    """Test constructor declarations and initialization."""
    
    def setUp(self):
        self.compiler = DafnyEVMCompiler(verify=False)
    
    def test_constructor_no_params(self):
        """Test constructor without parameters."""
        code = """
        class Token {
          var totalSupply: uint256
          
          constructor()
            modifies this
          {
            totalSupply := 1000000;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_constructor_with_params(self):
        """Test constructor with parameters."""
        code = """
        class Token {
          var totalSupply: uint256
          var owner: address
          
          constructor(supply: uint256)
            modifies this
          {
            totalSupply := supply;
            owner := msg.sender;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_constructor_with_precondition(self):
        """Test constructor with requires clause."""
        code = """
        class Token {
          var totalSupply: uint256
          
          constructor(supply: uint256)
            requires supply > 0
            modifies this
          {
            totalSupply := supply;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_constructor_initializes_mapping(self):
        """Test constructor initializing mapping."""
        code = """
        class Token {
          var balances: mapping<address, uint256>
          var totalSupply: uint256
          
          constructor(supply: uint256)
            modifies this
          {
            totalSupply := supply;
            balances := balances[msg.sender := supply];
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])


if __name__ == '__main__':
    unittest.main()
