"""
Tests for Solidity-compatible mappings.

Mappings are key-value stores: mapping<KeyType, ValueType>.
Supports nested mappings for complex data structures.
"""

import unittest
from src.dafny_compiler import DafnyEVMCompiler


class TestMappings(unittest.TestCase):
    """Test mapping declarations and operations."""
    
    def setUp(self):
        self.compiler = DafnyEVMCompiler(verify=False)
    
    def test_simple_mapping(self):
        """Test basic mapping declaration."""
        code = """
        class Token {
          var balances: mapping<address, uint256>
          
          method setBalance(addr: address, amount: uint256)
            modifies this
          {
            balances[addr] := amount;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_nested_mapping(self):
        """Test nested mapping (mapping of mappings)."""
        code = """
        class Token {
          var allowances: mapping<address, mapping<address, uint256>>
          
          method approve(spender: address, amount: uint256)
            modifies this
          {
            allowances[msg.sender][spender] := amount;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_mapping_access(self):
        """Test reading from mapping."""
        code = """
        class Token {
          var balances: mapping<address, uint256>
          
          method getBalance(addr: address) returns (balance: uint256)
          {
            return balances[addr];
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_mapping_in_operator(self):
        """Test 'in' operator for mapping existence check."""
        code = """
        class Registry {
          var registered: mapping<address, uint256>
          
          method isRegistered(addr: address) returns (exists: bool)
          {
            exists := addr in registered;
            return exists;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_mapping_update_functional_syntax(self):
        """Test functional map update syntax."""
        code = """
        class Token {
          var balances: mapping<address, uint256>
          
          method transfer(to: address, amount: uint256)
            modifies this
          {
            balances := balances[msg.sender := balances[msg.sender] - amount][to := balances[to] + amount];
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])


if __name__ == '__main__':
    unittest.main()
