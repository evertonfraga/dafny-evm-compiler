"""
Tests for ABI (Application Binary Interface) generation.

ABI defines how to interact with smart contracts from external applications.
"""

import unittest
import json
from src.dafny_compiler import DafnyEVMCompiler


class TestABIGeneration(unittest.TestCase):
    """Test ABI generation for various contract features."""
    
    def setUp(self):
        self.compiler = DafnyEVMCompiler(verify=False)
    
    def test_simple_function_abi(self):
        """Test ABI generation for simple function."""
        code = """
        class Test {
          method getValue() returns (v: uint256) {
            return 42;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
        
        abi = json.loads(result['abi'])
        functions = [e for e in abi if e['type'] == 'function']
        self.assertEqual(len(functions), 1)
        self.assertEqual(functions[0]['name'], 'getValue')
    
    def test_function_with_parameters(self):
        """Test ABI generation for function with parameters."""
        code = """
        class Test {
          method add(a: uint256, b: uint256) returns (result: uint256) {
            return a + b;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
        
        abi = json.loads(result['abi'])
        functions = [e for e in abi if e['type'] == 'function' and e['name'] == 'add']
        self.assertEqual(len(functions), 1)
        self.assertEqual(len(functions[0]['inputs']), 2)
    
    def test_constructor_abi(self):
        """Test ABI generation for constructor."""
        code = """
        class Test {
          var value: uint256
          
          constructor(initialValue: uint256)
            modifies this
          {
            value := initialValue;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
        
        abi = json.loads(result['abi'])
        constructors = [e for e in abi if e['type'] == 'constructor']
        self.assertEqual(len(constructors), 1)
        self.assertEqual(len(constructors[0]['inputs']), 1)
    
    def test_event_abi(self):
        """Test ABI generation for events."""
        code = """
        class Test {
          event Transfer(from: address, to: address, amount: uint256)
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
        
        abi = json.loads(result['abi'])
        events = [e for e in abi if e['type'] == 'event']
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['name'], 'Transfer')
    
    def test_multiple_return_values_abi(self):
        """Test ABI generation for multiple return values."""
        code = """
        class Test {
          method getValues() returns (a: uint256, b: uint256) {
            return 1, 2;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
        
        abi = json.loads(result['abi'])
        functions = [e for e in abi if e['type'] == 'function' and e['name'] == 'getValues']
        self.assertEqual(len(functions), 1)
        self.assertEqual(len(functions[0]['outputs']), 2)


if __name__ == '__main__':
    unittest.main()
