#!/usr/bin/env python3
"""
Isolate parser hang - test each feature
"""
import signal
import sys
from src.parser.dafny_parser import DafnyParser

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("TIMEOUT")

def test_parse(name, source, timeout=2):
    """Test parsing with timeout"""
    print(f"Testing: {name}...", end=" ")
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)
    try:
        parser = DafnyParser(source)
        contract = parser.parse()
        signal.alarm(0)
        print(f"✓ PASS (methods={len(contract.methods)})")
        return True
    except TimeoutException:
        signal.alarm(0)
        print(f"✗ HANG (timeout after {timeout}s)")
        return False
    except Exception as e:
        signal.alarm(0)
        print(f"✗ ERROR: {e}")
        return False

# Test cases
tests = [
    ("Basic class", """
class Token {
  var balance: uint256
}
"""),
    
    ("Mapping field", """
class Token {
  var balances: mapping<address, uint256>
}
"""),
    
    ("Constructor", """
class Token {
  constructor() {
    var x: uint256 := 0;
  }
}
"""),
    
    ("Simple method", """
class Token {
  method test() {
    var x: uint256 := 0;
  }
}
"""),
    
    ("Method with requires", """
class Token {
  method test(x: uint256)
    requires x > 0
  {
    var y: uint256 := x;
  }
}
"""),
    
    ("If statement", """
class Token {
  method test(x: uint256) {
    if x > 0 {
      var y: uint256 := x;
    }
  }
}
"""),
    
    ("Simple if expression", """
class Token {
  method test(x: uint256) returns (y: uint256) {
    return if x > 0 then 1 else 0;
  }
}
"""),
    
    ("Mapping access", """
class Token {
  var balances: mapping<address, uint256>
  method test(addr: address) returns (bal: uint256) {
    return balances[addr];
  }
}
"""),
    
    ("'in' in requires", """
class Token {
  var balances: mapping<address, uint256>
  method test(addr: address)
    requires addr in balances
  {
    var x: uint256 := 0;
  }
}
"""),
    
    ("'in' in if expression", """
class Token {
  var balances: mapping<address, uint256>
  method test(addr: address) returns (bal: uint256) {
    return if addr in balances then balances[addr] else 0;
  }
}
"""),
    
    ("'in' in var declaration", """
class Token {
  var balances: mapping<address, uint256>
  method test(addr: address) {
    var bal: uint256 := if addr in balances then balances[addr] else 0;
  }
}
"""),
]

if __name__ == "__main__":
    print("=" * 60)
    print("PARSER HANG ISOLATION TEST")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for name, source in tests:
        if test_parse(name, source, timeout=3):
            passed += 1
        else:
            failed += 1
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    sys.exit(0 if failed == 0 else 1)
