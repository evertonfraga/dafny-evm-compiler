"""
Tests for visibility modifiers: public, private, internal, external.
"""

import unittest
import json
from src.dafny_compiler import DafnyEVMCompiler


class TestVisibilityModifiers(unittest.TestCase):
    """Test visibility modifier declarations and ABI generation."""
    
    def setUp(self):
        self.compiler = DafnyEVMCompiler(verify=False)
    
    def test_public_method(self):
        """Test public method is in ABI."""
        code = """
        class Contract {
          method publicMethod() public returns (x: uint256) {
            return 42;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
        abi = json.loads(result['abi'])
        public_methods = [f for f in abi if f.get('name') == 'publicMethod']
        self.assertEqual(len(public_methods), 1)
    
    def test_external_method(self):
        """Test external method is in ABI."""
        code = """
        class Contract {
          method externalMethod() external returns (x: uint256) {
            return 42;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
        abi = json.loads(result['abi'])
        external_methods = [f for f in abi if f.get('name') == 'externalMethod']
        self.assertEqual(len(external_methods), 1)
    
    def test_private_method_not_in_abi(self):
        """Test private method is NOT in ABI."""
        code = """
        class Contract {
          method privateMethod() private returns (x: uint256) {
            return 42;
          }
          
          method callPrivate() public returns (x: uint256) {
            var result := privateMethod();
            return result;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
        abi = json.loads(result['abi'])
        private_methods = [f for f in abi if f.get('name') == 'privateMethod']
        self.assertEqual(len(private_methods), 0)
        public_methods = [f for f in abi if f.get('name') == 'callPrivate']
        self.assertEqual(len(public_methods), 1)
    
    def test_internal_method_not_in_abi(self):
        """Test internal method is NOT in ABI."""
        code = """
        class Contract {
          method internalMethod() internal returns (x: uint256) {
            return 42;
          }
          
          method callInternal() public returns (x: uint256) {
            var result := internalMethod();
            return result;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
        abi = json.loads(result['abi'])
        internal_methods = [f for f in abi if f.get('name') == 'internalMethod']
        self.assertEqual(len(internal_methods), 0)
        public_methods = [f for f in abi if f.get('name') == 'callInternal']
        self.assertEqual(len(public_methods), 1)
    
    def test_mixed_visibility(self):
        """Test contract with mixed visibility methods."""
        code = """
        class Contract {
          var value: uint256
          
          method publicGet() public returns (x: uint256) {
            return value;
          }
          
          method externalSet(v: uint256) external
            modifies this
          {
            value := v;
          }
          
          method internalHelper() internal returns (x: uint256) {
            return value * 2;
          }
          
          method privateHelper() private returns (x: uint256) {
            return value + 1;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
        abi = json.loads(result['abi'])
        method_names = [f.get('name') for f in abi if f.get('type') == 'function']
        self.assertIn('publicGet', method_names)
        self.assertIn('externalSet', method_names)
        self.assertNotIn('internalHelper', method_names)
        self.assertNotIn('privateHelper', method_names)
    
    def test_default_visibility_is_public(self):
        """Test that methods without visibility modifier default to public."""
        code = """
        class Contract {
          method defaultMethod() returns (x: uint256) {
            return 42;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
        abi = json.loads(result['abi'])
        default_methods = [f for f in abi if f.get('name') == 'defaultMethod']
        self.assertEqual(len(default_methods), 1)


if __name__ == '__main__':
    unittest.main()
