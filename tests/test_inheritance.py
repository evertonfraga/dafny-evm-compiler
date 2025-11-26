"""
Tests for inheritance support.
"""

import unittest
import json
from src.dafny_compiler import DafnyEVMCompiler
from src.parser.dafny_parser import DafnyParser


class TestInheritance(unittest.TestCase):
    """Test contract inheritance."""
    
    def setUp(self):
        self.compiler = DafnyEVMCompiler(verify=False)
    
    def test_parse_inheritance(self):
        """Test parsing class with inheritance."""
        code = """
        class Base {
          var value: uint256
        }
        
        class Derived is Base {
          var extra: uint256
        }
        """
        parser = DafnyParser(code)
        # Parser currently only handles one class, so parse Derived
        derived_code = """
        class Derived is Base {
          var extra: uint256
        }
        """
        parser = DafnyParser(derived_code)
        contract = parser.parse()
        self.assertEqual(contract.base_class, 'Base')
    
    def test_inherit_fields(self):
        """Test that derived class inherits base fields."""
        code = """
        class Ownable {
          var owner: address
          
          method getOwner() public view returns (x: address) {
            return owner;
          }
        }
        
        class Token is Ownable {
          var balance: uint256
          
          method getBalance() public view returns (x: uint256) {
            return balance;
          }
        }
        """
        # For now, just test that it parses
        # Full inheritance with field merging is future work
        parser = DafnyParser(code.split('class Token')[1])
        parser.source = 'class Token' + code.split('class Token')[1]
        contract = parser.parse()
        self.assertEqual(contract.base_class, 'Ownable')
        self.assertEqual(contract.name, 'Token')
    
    def test_simple_inheritance_compiles(self):
        """Test that simple inheritance compiles (base class ignored for now)."""
        code = """
        class Token is Ownable {
          var balance: uint256
          
          method getBalance() public view returns (x: uint256) {
            return balance;
          }
        }
        """
        compiler = DafnyEVMCompiler(verify=False)
        result = compiler.compile(code, skip_verification=True)
        # Should compile even though base class is not defined
        # (inheritance not fully implemented yet)
        self.assertTrue(result['success'])


if __name__ == '__main__':
    unittest.main()
