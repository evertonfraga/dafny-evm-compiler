"""
Tests for Solidity global variables.

Global variables provide access to blockchain state and transaction context.
Examples: msg.sender, msg.value, block.timestamp, block.number, tx.origin.
"""

import unittest
from src.dafny_compiler import DafnyEVMCompiler


class TestGlobalVariables(unittest.TestCase):
    """Test global variable access."""
    
    def setUp(self):
        self.compiler = DafnyEVMCompiler(verify=False)
    
    def test_msg_sender(self):
        """Test msg.sender access."""
        code = """
        class Contract {
          var owner: address
          
          method setOwner()
            modifies this
          {
            owner := msg.sender;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
        
        # Check Yul contains caller()
        yul = result.get('yul_code', '')
        self.assertIn("caller()", yul)
    
    def test_msg_value(self):
        """Test msg.value access."""
        code = """
        class Payable {
          var received: uint256
          
          method deposit() payable
            modifies this
          {
            received := msg.value;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_block_timestamp(self):
        """Test block.timestamp access."""
        code = """
        class TimeLock {
          var unlockTime: uint256
          
          method setUnlockTime(duration: uint256)
            modifies this
          {
            unlockTime := block.timestamp + duration;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_block_number(self):
        """Test block.number access."""
        code = """
        class Contract {
          var createdAt: uint256
          
          method recordBlock()
            modifies this
          {
            createdAt := block.number;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])


if __name__ == '__main__':
    unittest.main()
