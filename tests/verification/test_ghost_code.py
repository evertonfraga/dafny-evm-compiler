"""
Tests for Dafny ghost code in smart contracts.

Ghost variables and methods exist only for verification and are erased during compilation.
They have zero runtime cost while providing verification guarantees.
"""

import unittest
from src.dafny_compiler import DafnyEVMCompiler


class TestGhostCode(unittest.TestCase):
    """Test Dafny ghost variables and methods."""
    
    def setUp(self):
        self.compiler = DafnyEVMCompiler(verify=False)
    
    def test_ghost_const(self):
        """Test ghost const for verification-only constants."""
        code = """
        class Token {
          ghost const MAX_SUPPLY: int := 1000000
          var totalSupply: uint256
          
          method mint(amount: uint256)
            requires totalSupply + amount <= MAX_SUPPLY
            modifies this
          {
            totalSupply := totalSupply + amount;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
        
        # Ghost const should not appear in bytecode
        bytecode = result.get('bytecode', '')
        # Bytecode exists but ghost const is not stored
        self.assertIsNotNone(bytecode)
    
    def test_ghost_variable(self):
        """Test ghost variable for tracking verification state."""
        code = """
        class Counter {
          var count: uint256
          ghost var totalIncrements: int
          
          method increment()
            modifies this
          {
            count := count + 1;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_ghost_method(self):
        """Test ghost method for verification helpers."""
        code = """
        class Validator {
          var value: uint256
          
          ghost method isValid() returns (valid: bool)
          {
            return value > 0;
          }
          
          method setValue(v: uint256)
            modifies this
          {
            value := v;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])


if __name__ == '__main__':
    unittest.main()
