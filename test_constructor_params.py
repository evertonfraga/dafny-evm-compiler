#!/usr/bin/env python3
"""TDD: Constructor with parameters support"""

import sys
sys.path.insert(0, 'src')
from parser.dafny_parser import DafnyParser

def test_constructor_with_parameter():
    """Test parsing constructor with parameter"""
    code = """
class Token {
  var supply: uint256
  
  constructor(initialSupply: uint256)
  {
    supply := initialSupply;
  }
}
"""
    parser = DafnyParser(code)
    ast = parser.parse()
    
    assert ast.constructor is not None, "Constructor should be parsed"
    assert len(ast.constructor.params) == 1, f"Expected 1 param, got {len(ast.constructor.params)}"
    assert ast.constructor.params[0].name == "initialSupply", f"Expected 'initialSupply', got {ast.constructor.params[0].name}"
    param_type = str(ast.constructor.params[0].type)
    assert "uint256" in param_type, f"Expected 'uint256' in type, got {param_type}"
    print("✓ test_constructor_with_parameter")

def test_constructor_yul_generation():
    """Test Yul generation for constructor with parameter"""
    import subprocess
    import tempfile
    import os
    
    code = """class Token {
  var supply: uint256
  
  constructor(initialSupply: uint256)
  {
    supply := initialSupply;
  }
}"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.dfy', delete=False) as f:
        f.write(code)
        f.flush()
        
        result = subprocess.run(
            ['python3', 'cli.py', f.name, '--yul-only', '--skip-verification'],
            capture_output=True, text=True
        )
        
        os.unlink(f.name)
        
        assert result.returncode == 0, f"Compilation failed: {result.stdout}"
        
        # Read generated Yul
        with open('build/Token.yul', 'r') as yul_file:
            yul = yul_file.read()
        
        assert "calldataload" in yul, "Constructor should load parameter from calldata"
        assert "initialSupply" in yul, "Constructor parameter should be available"
        print("✓ test_constructor_yul_generation")

if __name__ == "__main__":
    print("=" * 60)
    print("TDD: Constructor Parameters")
    print("=" * 60)
    
    tests = [
        test_constructor_with_parameter,
        test_constructor_yul_generation,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: {e}")
            failed += 1
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    sys.exit(0 if failed == 0 else 1)
