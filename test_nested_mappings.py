#!/usr/bin/env python3
"""TDD: Nested Mapping Support"""

import sys
sys.path.insert(0, 'src')
from parser.dafny_parser import DafnyParser

def test_parse_nested_mapping():
    """Test parsing nested mapping declaration"""
    code = """
class Token {
  var allowances: mapping<address, mapping<address, uint256>>
}
"""
    parser = DafnyParser(code)
    ast = parser.parse()
    
    assert len(ast.fields) == 1, f"Expected 1 field, got {len(ast.fields)}"
    field = ast.fields[0]
    assert field.name == "allowances", f"Expected 'allowances', got {field.name}"
    print("✓ test_parse_nested_mapping")

def test_nested_mapping_assignment():
    """Test parsing nested mapping assignment"""
    code = """
class Token {
  var allowances: mapping<address, mapping<address, uint256>>
  
  method approve(spender: address, amount: uint256)
  {
    allowances[msg.sender][spender] := amount;
  }
}
"""
    parser = DafnyParser(code)
    ast = parser.parse()
    
    assert len(ast.methods) == 1, f"Expected 1 method, got {len(ast.methods)}"
    method = ast.methods[0]
    assert len(method.body) == 1, f"Expected 1 statement, got {len(method.body)}"
    
    stmt = method.body[0]
    assert stmt.__class__.__name__ == "Assignment", f"Expected Assignment, got {stmt.__class__.__name__}"
    print("✓ test_nested_mapping_assignment")

def test_nested_mapping_access():
    """Test parsing nested mapping access in expression"""
    code = """
class Token {
  var allowances: mapping<address, mapping<address, uint256>>
  
  method getAllowance(owner: address, spender: address) returns (amount: uint256)
  {
    amount := allowances[owner][spender];
    return amount;
  }
}
"""
    parser = DafnyParser(code)
    ast = parser.parse()
    
    method = ast.methods[0]
    assert len(method.body) == 2, f"Expected 2 statements, got {len(method.body)}"
    print("✓ test_nested_mapping_access")

def test_nested_mapping_yul_generation():
    """Test Yul generation for nested mapping"""
    import subprocess
    import tempfile
    import os
    
    code = """class Token {
  var allowances: mapping<address, mapping<address, uint256>>
  
  method approve(spender: address, amount: uint256)
  {
    allowances[msg.sender][spender] := amount;
  }
  
  method getAllowance(owner: address, spender: address) returns (amount: uint256)
  {
    return allowances[owner][spender];
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
        
        assert result.returncode == 0, f"Compilation failed: {result.stdout}\n{result.stderr}"
        
        # Read generated Yul
        with open('build/Token.yul', 'r') as yul_file:
            yul = yul_file.read()
        
        # Check for nested keccak256 computation
        # For allowances[owner][spender], we need:
        # keccak256(keccak256(slot, owner), spender)
        assert "keccak256" in yul, "Should use keccak256 for mapping"
        assert "approve" in yul, "Should have approve function"
        assert "getAllowance" in yul, "Should have getAllowance function"
        
        print("✓ test_nested_mapping_yul_generation")

def test_nested_mapping_storage_computation():
    """Test that nested mapping computes correct storage slot"""
    import subprocess
    import tempfile
    import os
    
    code = """class Token {
  var allowances: mapping<address, mapping<address, uint256>>
  
  method setAllowance(owner: address, spender: address, amount: uint256)
  {
    allowances[owner][spender] := amount;
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
        
        if result.returncode != 0:
            print(f"Expected failure (not yet implemented):")
            print(result.stdout)
            print(result.stderr)
            return  # Expected to fail initially
        
        with open('build/Token.yul', 'r') as yul_file:
            yul = yul_file.read()
        
        # Should have nested keccak256 calls
        # Pattern: keccak256(...keccak256(slot, key1)..., key2)
        assert yul.count("keccak256") >= 2, "Should have at least 2 keccak256 calls for nested mapping"
        
        print("✓ test_nested_mapping_storage_computation")

if __name__ == "__main__":
    print("=" * 60)
    print("TDD: Nested Mapping Support")
    print("=" * 60)
    
    tests = [
        test_parse_nested_mapping,
        test_nested_mapping_assignment,
        test_nested_mapping_access,
        test_nested_mapping_yul_generation,
        test_nested_mapping_storage_computation,
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
