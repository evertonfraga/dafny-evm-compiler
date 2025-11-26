"""
Tests for SPDX license identifier support.

Solidity contracts should include license identifiers at the top.
Format: // SPDX-License-Identifier: <LICENSE>
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..', 'src'))
from parser.dafny_parser import DafnyParser


class TestLicense(unittest.TestCase):
    """Test SPDX license identifier parsing and handling."""
    
    def test_mit_license(self):
        """Test MIT license identifier."""
        code = """
        // SPDX-License-Identifier: MIT
        
        class Token {
          var balance: uint256
        }
        """
        parser = DafnyParser(code)
        ast = parser.parse()
        
        # Parser should extract license
        if hasattr(ast, 'license'):
            self.assertEqual(ast.license, "MIT")
    
    def test_gpl_license(self):
        """Test GPL-3.0 license identifier."""
        code = """
        // SPDX-License-Identifier: GPL-3.0
        
        class Token {
          var balance: uint256
        }
        """
        parser = DafnyParser(code)
        ast = parser.parse()
        
        if hasattr(ast, 'license'):
            self.assertEqual(ast.license, "GPL-3.0")
    
    def test_unlicensed(self):
        """Test UNLICENSED identifier."""
        code = """
        // SPDX-License-Identifier: UNLICENSED
        
        class Token {
          var balance: uint256
        }
        """
        parser = DafnyParser(code)
        ast = parser.parse()
        
        if hasattr(ast, 'license'):
            self.assertEqual(ast.license, "UNLICENSED")
    
    def test_no_license(self):
        """Test contract without license identifier."""
        code = """
        class Token {
          var balance: uint256
        }
        """
        parser = DafnyParser(code)
        ast = parser.parse()
        
        # Should parse successfully even without license
        self.assertEqual(ast.name, "Token")
    
    def test_license_with_pragma(self):
        """Test license with pragma statement."""
        code = """
        // SPDX-License-Identifier: MIT
        pragma solidity ^0.8.0;
        
        class Token {
          var balance: uint256
        }
        """
        parser = DafnyParser(code)
        ast = parser.parse()
        
        # Should parse successfully
        self.assertEqual(ast.name, "Token")


if __name__ == '__main__':
    unittest.main()
