"""
Unit tests for parser features - isolate what causes hangs
"""
import pytest
import signal
from src.parser.dafny_parser import DafnyParser

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Parser timeout")

def parse_with_timeout(source, timeout=2):
    """Parse with timeout to catch infinite loops"""
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)
    try:
        parser = DafnyParser(source)
        contract = parser.parse()
        signal.alarm(0)
        return contract
    except TimeoutException:
        signal.alarm(0)
        raise

def test_basic_class():
    """Test: Basic class declaration"""
    source = """
class Token {
  var balance: uint256
}
"""
    contract = parse_with_timeout(source)
    assert contract.name == "Token"
    assert len(contract.fields) == 1

def test_mapping_field():
    """Test: Mapping field declaration"""
    source = """
class Token {
  var balances: mapping<address, uint256>
}
"""
    contract = parse_with_timeout(source)
    assert len(contract.fields) == 1
    assert contract.fields[0].name == "balances"

def test_constructor():
    """Test: Constructor"""
    source = """
class Token {
  var supply: uint256
  
  constructor() {
    supply := 1000;
  }
}
"""
    contract = parse_with_timeout(source)
    assert contract.constructor is not None

def test_method_with_requires():
    """Test: Method with requires"""
    source = """
class Token {
  method mint(amount: uint256)
    requires amount > 0
  {
    var x: uint256 := amount;
  }
}
"""
    contract = parse_with_timeout(source)
    assert len(contract.methods) == 1
    assert len(contract.methods[0].preconditions) == 1

def test_method_with_ensures():
    """Test: Method with ensures"""
    source = """
class Token {
  var supply: uint256
  
  method mint(amount: uint256)
    ensures supply == old(supply) + amount
  {
    supply := supply + amount;
  }
}
"""
    contract = parse_with_timeout(source)
    assert len(contract.methods) == 1
    assert len(contract.methods[0].postconditions) == 1

def test_if_statement():
    """Test: If statement"""
    source = """
class Token {
  method test(x: uint256) {
    if x > 0 {
      var y: uint256 := x;
    }
  }
}
"""
    contract = parse_with_timeout(source)
    assert len(contract.methods) == 1

def test_if_expression_simple():
    """Test: Simple if expression"""
    source = """
class Token {
  method test(x: uint256) returns (y: uint256) {
    return if x > 0 then 1 else 0;
  }
}
"""
    contract = parse_with_timeout(source)
    assert len(contract.methods) == 1

def test_if_expression_with_in():
    """Test: If expression with 'in' operator - THIS MAY HANG"""
    source = """
class Token {
  var balances: mapping<address, uint256>
  
  method test(addr: address) returns (bal: uint256) {
    return if addr in balances then balances[addr] else 0;
  }
}
"""
    try:
        contract = parse_with_timeout(source, timeout=3)
        assert len(contract.methods) == 1
    except TimeoutException:
        pytest.fail("Parser hangs on 'if...in...then...else' expression")

def test_var_with_if_expression():
    """Test: Variable declaration with if expression"""
    source = """
class Token {
  var balances: mapping<address, uint256>
  
  method test(addr: address) {
    var bal: uint256 := if addr in balances then balances[addr] else 0;
  }
}
"""
    try:
        contract = parse_with_timeout(source, timeout=3)
        assert len(contract.methods) == 1
    except TimeoutException:
        pytest.fail("Parser hangs on var with 'if...in' expression")

def test_mapping_access():
    """Test: Simple mapping access"""
    source = """
class Token {
  var balances: mapping<address, uint256>
  
  method test(addr: address) returns (bal: uint256) {
    return balances[addr];
  }
}
"""
    contract = parse_with_timeout(source)
    assert len(contract.methods) == 1

def test_mapping_assignment():
    """Test: Mapping assignment"""
    source = """
class Token {
  var balances: mapping<address, uint256>
  
  method test(addr: address, amount: uint256) {
    balances[addr] := amount;
  }
}
"""
    contract = parse_with_timeout(source)
    assert len(contract.methods) == 1

def test_in_operator_in_requires():
    """Test: 'in' operator in requires clause"""
    source = """
class Token {
  var balances: mapping<address, uint256>
  
  method test(addr: address)
    requires addr in balances
  {
    var x: uint256 := 0;
  }
}
"""
    try:
        contract = parse_with_timeout(source, timeout=3)
        assert len(contract.methods) == 1
    except TimeoutException:
        pytest.fail("Parser hangs on 'in' in requires")

def test_in_operator_in_ensures():
    """Test: 'in' operator in ensures clause"""
    source = """
class Token {
  var balances: mapping<address, uint256>
  
  method test(addr: address) returns (result: bool)
    ensures result == (addr in balances)
  {
    return addr in balances;
  }
}
"""
    try:
        contract = parse_with_timeout(source, timeout=3)
        assert len(contract.methods) == 1
    except TimeoutException:
        pytest.fail("Parser hangs on 'in' in ensures")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
