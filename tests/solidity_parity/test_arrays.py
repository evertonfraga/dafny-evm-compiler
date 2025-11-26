"""
Tests for Solidity-compatible arrays.

Supports dynamic arrays with push, pop, and length operations.
"""

import unittest
from src.dafny_compiler import DafnyEVMCompiler


class TestArrays(unittest.TestCase):
    """Test array declarations and operations."""
    
    def setUp(self):
        self.compiler = DafnyEVMCompiler(verify=False)
    
    def test_array_declaration(self):
        """Test basic array declaration."""
        code = """
        class Contract {
          var items: array<uint256>
          
          method addItem(item: uint256)
            modifies this
          {
            items.push(item);
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_array_access(self):
        """Test array element access."""
        code = """
        class Contract {
          var items: array<uint256>
          
          method getItem(index: uint256) returns (item: uint256)
          {
            return items[index];
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_array_push(self):
        """Test array push operation."""
        code = """
        class Stack {
          var values: array<uint256>
          
          method push(value: uint256)
            modifies this
          {
            values.push(value);
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_array_pop(self):
        """Test array pop operation."""
        code = """
        class Stack {
          var values: array<uint256>
          
          method pop()
            modifies this
          {
            values.pop();
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_array_length(self):
        """Test array length property."""
        code = """
        class Contract {
          var items: array<uint256>
          
          method getLength() returns (len: uint256)
          {
            return items.length;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])


if __name__ == '__main__':
    unittest.main()
