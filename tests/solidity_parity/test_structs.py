"""
Tests for Solidity-compatible struct declarations.

Structs allow grouping related data into custom types.
"""

import unittest
from src.dafny_compiler import DafnyEVMCompiler


class TestStructs(unittest.TestCase):
    """Test struct declarations and usage."""
    
    def setUp(self):
        self.compiler = DafnyEVMCompiler(verify=False)
    
    def test_struct_declaration(self):
        """Test basic struct declaration."""
        code = """
        struct Person {
          age: uint256
          balance: uint256
        }
        
        class Test {
          var owner: Person
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_struct_field_access(self):
        """Test accessing struct fields."""
        code = """
        struct Person {
          age: uint256
          balance: uint256
        }
        
        class Test {
          var owner: Person
          
          method setAge(newAge: uint256)
            modifies this
          {
            owner.age := newAge;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_struct_initialization(self):
        """Test struct initialization."""
        code = """
        struct Point {
          x: uint256
          y: uint256
        }
        
        class Test {
          var position: Point
          
          method setPosition(newX: uint256, newY: uint256)
            modifies this
          {
            position.x := newX;
            position.y := newY;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_multiple_structs(self):
        """Test multiple struct declarations."""
        code = """
        struct Person {
          age: uint256
        }
        
        struct Company {
          employees: uint256
        }
        
        class Test {
          var ceo: Person
          var company: Company
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])


if __name__ == '__main__':
    unittest.main()
