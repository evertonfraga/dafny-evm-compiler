"""
Tests for inter-contract calls.
Note: Full inter-contract call support is complex and requires:
- Contract type system
- External call encoding
- Return value decoding
For now, we test basic parsing and compilation.
"""

import unittest
from src.dafny_compiler import DafnyEVMCompiler


class TestInterContractCalls(unittest.TestCase):
    """Test calling methods on other contracts."""
    
    def setUp(self):
        self.compiler = DafnyEVMCompiler(verify=False)
    
    def test_low_level_call(self):
        """Test low-level call to external contract."""
        code = """
        class Caller {
          method callExternal(target: address) public returns (success: bool) {
            var result := target.call("");
            return true;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_delegatecall(self):
        """Test delegatecall to external contract."""
        code = """
        class Caller {
          method delegateCall(target: address) public returns (success: bool) {
            var result := target.delegatecall("");
            return true;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_staticcall(self):
        """Test staticcall to external contract."""
        code = """
        class Caller {
          method staticCall(target: address) public returns (success: bool) {
            var result := target.staticcall("");
            return true;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])


if __name__ == '__main__':
    unittest.main()
