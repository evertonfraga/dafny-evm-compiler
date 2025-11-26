"""
Tests for state mutability: view, pure, payable.
"""

import unittest
import json
from src.dafny_compiler import DafnyEVMCompiler


class TestStateMutability(unittest.TestCase):
    """Test state mutability modifiers."""
    
    def setUp(self):
        self.compiler = DafnyEVMCompiler(verify=False)
    
    def test_view_method(self):
        """Test view method in ABI."""
        code = """
        class Contract {
          var value: uint256
          
          method getValue() view returns (x: uint256) {
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
    
    def test_pure_method(self):
        """Test pure method in ABI."""
        code = """
        class Contract {
          method add(a: uint256, b: uint256) pure returns (x: uint256) {
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
    
    def test_payable_method(self):
        """Test payable method in ABI."""
        code = """
        class Contract {
          var balance: uint256
          
          method deposit() payable
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
    
    def test_nonpayable_method(self):
        """Test nonpayable method (default) in ABI."""
        code = """
        class Contract {
          var value: uint256
          
          method setValue(v: uint256)
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
        self.assertEqual(methods[0]['stateMutability'], 'nonpayable')
    
    def test_mixed_mutability(self):
        """Test contract with mixed state mutability."""
        code = """
        class Contract {
          var value: uint256
          
          method getValue() view returns (x: uint256) {
            return value;
          }
          
          method add(a: uint256, b: uint256) pure returns (x: uint256) {
            return a + b;
          }
          
          method setValue(v: uint256)
            modifies this
          {
            value := v;
          }
          
          method deposit() payable
            modifies this
          {
            value := value + msg.value;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
        abi = json.loads(result['abi'])
        
        get_value = [f for f in abi if f.get('name') == 'getValue'][0]
        self.assertEqual(get_value['stateMutability'], 'view')
        
        add = [f for f in abi if f.get('name') == 'add'][0]
        self.assertEqual(add['stateMutability'], 'pure')
        
        set_value = [f for f in abi if f.get('name') == 'setValue'][0]
        self.assertEqual(set_value['stateMutability'], 'nonpayable')
        
        deposit = [f for f in abi if f.get('name') == 'deposit'][0]
        self.assertEqual(deposit['stateMutability'], 'payable')


if __name__ == '__main__':
    unittest.main()
