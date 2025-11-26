"""
Tests for complex modifier combinations.
"""

import unittest
import json
from src.dafny_compiler import DafnyEVMCompiler


class TestModifierCombinations(unittest.TestCase):
    """Test combinations of visibility, mutability, and custom modifiers."""
    
    def setUp(self):
        self.compiler = DafnyEVMCompiler(verify=False)
    
    def test_public_view(self):
        """Test public view method."""
        code = """
        class Contract {
          var value: uint256
          
          method getValue() public view returns (x: uint256) {
            return value;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
        abi = json.loads(result['abi'])
        methods = [f for f in abi if f.get('name') == 'getValue']
        self.assertEqual(len(methods), 1)
        self.assertEqual(methods[0]['stateMutability'], 'view')
    
    def test_external_payable(self):
        """Test external payable method."""
        code = """
        class Contract {
          var balance: uint256
          
          method deposit() external payable
            modifies this
          {
            balance := balance + msg.value;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
        abi = json.loads(result['abi'])
        methods = [f for f in abi if f.get('name') == 'deposit']
        self.assertEqual(len(methods), 1)
        self.assertEqual(methods[0]['stateMutability'], 'payable')
    
    def test_public_with_custom_modifier(self):
        """Test public method with custom modifier."""
        code = """
        class Contract {
          var owner: address
          var value: uint256
          
          modifier onlyOwner {
            require msg.sender == owner;
            _;
          }
          
          method setValue(v: uint256) public onlyOwner
            modifies this
          {
            value := v;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
        abi = json.loads(result['abi'])
        methods = [f for f in abi if f.get('name') == 'setValue']
        self.assertEqual(len(methods), 1)
    
    def test_external_pure(self):
        """Test external pure method."""
        code = """
        class Contract {
          method add(a: uint256, b: uint256) external pure returns (x: uint256) {
            return a + b;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
        abi = json.loads(result['abi'])
        methods = [f for f in abi if f.get('name') == 'add']
        self.assertEqual(len(methods), 1)
        self.assertEqual(methods[0]['stateMutability'], 'pure')
    
    def test_private_pure(self):
        """Test private pure helper method."""
        code = """
        class Contract {
          method calculate(a: uint256, b: uint256) private pure returns (x: uint256) {
            return a * b + 10;
          }
          
          method useCalculate(a: uint256, b: uint256) public pure returns (x: uint256) {
            var result := calculate(a, b);
            return result;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
        abi = json.loads(result['abi'])
        # Private method should not be in ABI
        private_methods = [f for f in abi if f.get('name') == 'calculate']
        self.assertEqual(len(private_methods), 0)
        # Public method should be in ABI
        public_methods = [f for f in abi if f.get('name') == 'useCalculate']
        self.assertEqual(len(public_methods), 1)
        self.assertEqual(public_methods[0]['stateMutability'], 'pure')
    
    def test_multiple_modifiers_with_visibility(self):
        """Test method with multiple custom modifiers and visibility."""
        code = """
        class Contract {
          var owner: address
          var paused: bool
          var value: uint256
          
          modifier onlyOwner {
            require msg.sender == owner;
            _;
          }
          
          modifier whenNotPaused {
            require paused == false;
            _;
          }
          
          method setValue(v: uint256) public onlyOwner whenNotPaused
            modifies this
          {
            value := v;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
        abi = json.loads(result['abi'])
        methods = [f for f in abi if f.get('name') == 'setValue']
        self.assertEqual(len(methods), 1)


if __name__ == '__main__':
    unittest.main()
