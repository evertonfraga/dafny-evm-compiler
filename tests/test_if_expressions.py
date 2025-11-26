"""
TDD: If expression support in Yul generation
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.parser.dafny_parser import DafnyParser
from src.translator.yul_generator import YulGenerator

def test_simple_if_expression_in_return():
    """Test: return if x > 0 then 1 else 0"""
    source = """
class Test {
  method test(x: uint256) returns (y: uint256) {
    return if x > 0 then 1 else 0;
  }
}
"""
    parser = DafnyParser(source)
    contract = parser.parse()
    generator = YulGenerator()
    yul = generator.generate(contract)
    
    # Should generate Yul switch or if statement, not Dafny syntax
    assert "if x > 0 then" not in yul
    assert "switch" in yul or "if gt(x, 0)" in yul
    print("✓ test_simple_if_expression_in_return")

def test_if_expression_in_var_declaration():
    """Test: var y := if x > 0 then 1 else 0"""
    source = """
class Test {
  method test(x: uint256) {
    var y: uint256 := if x > 0 then 1 else 0;
  }
}
"""
    parser = DafnyParser(source)
    contract = parser.parse()
    generator = YulGenerator()
    yul = generator.generate(contract)
    
    assert "if x > 0 then" not in yul
    assert "let y :=" in yul
    print("✓ test_if_expression_in_var_declaration")

def test_if_expression_with_mapping_access():
    """Test: var bal := if addr in balances then balances[addr] else 0"""
    source = """
class Test {
  var balances: mapping<address, uint256>
  
  method test(addr: address) {
    var bal: uint256 := if addr in balances then balances[addr] else 0;
  }
}
"""
    parser = DafnyParser(source)
    contract = parser.parse()
    generator = YulGenerator()
    yul = generator.generate(contract)
    
    assert "if addr in balances then" not in yul
    assert "let bal :=" in yul
    print("✓ test_if_expression_with_mapping_access")

def test_nested_if_expression():
    """Test: nested if expressions"""
    source = """
class Test {
  method test(x: uint256, y: uint256) returns (z: uint256) {
    return if x > 0 then (if y > 0 then 1 else 2) else 3;
  }
}
"""
    parser = DafnyParser(source)
    contract = parser.parse()
    generator = YulGenerator()
    yul = generator.generate(contract)
    
    assert "if x > 0 then" not in yul
    print("✓ test_nested_if_expression")

def test_if_expression_in_assignment():
    """Test: x := if y > 0 then 1 else 0"""
    source = """
class Test {
  var value: uint256
  
  method test(y: uint256) {
    value := if y > 0 then 1 else 0;
  }
}
"""
    parser = DafnyParser(source)
    contract = parser.parse()
    generator = YulGenerator()
    yul = generator.generate(contract)
    
    assert "if y > 0 then" not in yul
    assert "sstore" in yul
    print("✓ test_if_expression_in_assignment")

if __name__ == "__main__":
    print("=" * 60)
    print("TDD: If Expression Support")
    print("=" * 60)
    
    tests = [
        test_simple_if_expression_in_return,
        test_if_expression_in_var_declaration,
        test_if_expression_with_mapping_access,
        test_nested_if_expression,
        test_if_expression_in_assignment,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: ERROR - {e}")
            failed += 1
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    sys.exit(0 if failed == 0 else 1)
