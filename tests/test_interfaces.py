"""
Tests for interface support.
"""

import unittest
from src.parser.dafny_parser import DafnyParser
from src.dafny_compiler import DafnyEVMCompiler


class TestInterfaces(unittest.TestCase):
    """Test interface declarations and implementations."""
    
    def test_parse_interface(self):
        """Test parsing interface declaration."""
        code = """
        interface IERC20 {
          method transfer(to: address, amount: uint256) returns (success: bool);
          method balanceOf(account: address) view returns (balance: uint256);
        }
        """
        parser = DafnyParser(code)
        result = parser.parse()
        # For now, interfaces might be parsed as contracts
        self.assertIsNotNone(result)
    
    def test_interface_with_events(self):
        """Test interface with event declarations."""
        code = """
        interface IERC20 {
          event Transfer(from: address, to: address, amount: uint256)
          
          method transfer(to: address, amount: uint256) returns (success: bool);
        }
        """
        parser = DafnyParser(code)
        result = parser.parse()
        self.assertIsNotNone(result)
    
    def test_contract_implements_interface(self):
        """Test contract implementing an interface."""
        code = """
        class Token is IERC20 {
          var balances: mapping<address, uint256>
          
          method transfer(to: address, amount: uint256) public returns (success: bool)
            modifies this
          {
            return true;
          }
          
          method balanceOf(account: address) public view returns (balance: uint256) {
            return balances[account];
          }
        }
        """
        compiler = DafnyEVMCompiler(verify=False)
        result = compiler.compile(code, skip_verification=True)
        # Should compile (interface name treated as base class for now)
        self.assertTrue(result['success'])


if __name__ == '__main__':
    unittest.main()
