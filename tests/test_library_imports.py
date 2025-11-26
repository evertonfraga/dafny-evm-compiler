"""
Tests for library import parsing.
Note: This is parsing only - no code generation for libraries yet.
"""

import unittest
from src.dafny_compiler import DafnyEVMCompiler
from src.parser.dafny_parser import DafnyParser


class TestLibraryImports(unittest.TestCase):
    """Test library import statement parsing."""
    
    def test_simple_import(self):
        """Test parsing simple import statement."""
        code = """
        import SafeMath
        
        class Token {
          var balance: uint256
        }
        """
        parser = DafnyParser(code)
        contract = parser.parse()
        self.assertIsNotNone(contract)
        self.assertTrue(hasattr(contract, 'imports'))
        self.assertEqual(len(contract.imports), 1)
        self.assertEqual(contract.imports[0], 'SafeMath')
    
    def test_multiple_imports(self):
        """Test parsing multiple import statements."""
        code = """
        import SafeMath
        import Ownable
        import Pausable
        
        class Token {
          var balance: uint256
        }
        """
        parser = DafnyParser(code)
        contract = parser.parse()
        self.assertEqual(len(contract.imports), 3)
        self.assertIn('SafeMath', contract.imports)
        self.assertIn('Ownable', contract.imports)
        self.assertIn('Pausable', contract.imports)
    
    def test_import_with_path(self):
        """Test parsing import with file path."""
        code = """
        import "./libraries/SafeMath.dfy"
        
        class Token {
          var balance: uint256
        }
        """
        parser = DafnyParser(code)
        contract = parser.parse()
        self.assertEqual(len(contract.imports), 1)
        self.assertEqual(contract.imports[0], './libraries/SafeMath.dfy')
    
    def test_contract_compiles_with_imports(self):
        """Test that contract with imports compiles (imports are ignored for now)."""
        code = """
        import SafeMath
        
        class Token {
          var balance: uint256
          
          method getBalance() public view returns (x: uint256) {
            return balance;
          }
        }
        """
        compiler = DafnyEVMCompiler(verify=False)
        result = compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])


if __name__ == '__main__':
    unittest.main()
