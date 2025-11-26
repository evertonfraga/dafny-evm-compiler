"""
Tests for Solidity-compatible data types.

Supports: uint8-uint256, int8-int256, address, bool, bytes, bytes32, string.
"""

import unittest
from src.dafny_compiler import DafnyEVMCompiler


class TestTypes(unittest.TestCase):
    """Test Solidity-compatible type declarations."""
    
    def setUp(self):
        self.compiler = DafnyEVMCompiler(verify=False)
    
    def test_uint_types(self):
        """Test various uint types."""
        code = """
        class Types {
          var u8: uint8
          var u16: uint16
          var u32: uint32
          var u64: uint64
          var u128: uint128
          var u256: uint256
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_int_types(self):
        """Test signed integer types."""
        code = """
        class Types {
          var i8: int8
          var i16: int16
          var i32: int32
          var i64: int64
          var i128: int128
          var i256: int256
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_address_type(self):
        """Test address type."""
        code = """
        class Contract {
          var owner: address
          var recipient: address
          
          method transfer(to: address)
            modifies this
          {
            recipient := to;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_bool_type(self):
        """Test boolean type."""
        code = """
        class Contract {
          var active: bool
          var paused: bool
          
          method toggle()
            modifies this
          {
            active := !active;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_bytes_types(self):
        """Test bytes and bytes32 types."""
        code = """
        class Contract {
          var data: bytes32
          var hash: bytes32
          
          method setData(d: bytes32)
            modifies this
          {
            data := d;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])


if __name__ == '__main__':
    unittest.main()
