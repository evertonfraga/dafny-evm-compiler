import pytest
from src.parser.dafny_parser import DafnyParser
from src.translator.yul_generator import YulGenerator

def test_indexed_event_parsing():
    """Test parsing events with indexed parameters"""
    source = """
    class Token {
        event Transfer(address indexed from, address indexed to, uint256 amount)
    }
    """
    parser = DafnyParser(source)
    contract = parser.parse()
    
    assert len(contract.events) == 1
    event = contract.events[0]
    assert event.name == "Transfer"
    assert len(event.params) == 3
    assert event.indexed == [True, True, False]
    assert event.anonymous == False

def test_anonymous_event_parsing():
    """Test parsing anonymous events"""
    source = """
    class Token {
        event Data(uint256 value) anonymous
    }
    """
    parser = DafnyParser(source)
    contract = parser.parse()
    
    assert len(contract.events) == 1
    event = contract.events[0]
    assert event.name == "Data"
    assert event.anonymous == True

def test_custom_error_parsing():
    """Test parsing custom errors"""
    source = """
    class Token {
        error InsufficientBalance(uint256 requested, uint256 available)
        error Unauthorized(address caller)
    }
    """
    parser = DafnyParser(source)
    contract = parser.parse()
    
    assert len(contract.errors) == 2
    assert contract.errors[0].name == "InsufficientBalance"
    assert len(contract.errors[0].params) == 2
    assert contract.errors[1].name == "Unauthorized"

def test_revert_with_error():
    """Test parsing revert with custom error"""
    source = """
    class Token {
        error InsufficientBalance(uint256 requested, uint256 available)
        
        method transfer(amount: uint256) {
            revert InsufficientBalance(amount, 100);
        }
    }
    """
    parser = DafnyParser(source)
    contract = parser.parse()
    
    method = contract.methods[0]
    assert len(method.body) == 1
    stmt = method.body[0]
    assert stmt.error_name == "InsufficientBalance"
    assert len(stmt.error_args) == 2

def test_revert_with_message():
    """Test parsing revert with message"""
    source = """
    class Token {
        method transfer(amount: uint256) {
            revert("Insufficient balance");
        }
    }
    """
    parser = DafnyParser(source)
    contract = parser.parse()
    
    method = contract.methods[0]
    stmt = method.body[0]
    assert stmt.message == "Insufficient balance"

def test_selfdestruct_parsing():
    """Test parsing selfdestruct"""
    source = """
    class Token {
        method destroy(recipient: address) {
            selfdestruct(recipient);
        }
    }
    """
    parser = DafnyParser(source)
    contract = parser.parse()
    
    method = contract.methods[0]
    assert len(method.body) == 1

def test_receive_function_parsing():
    """Test parsing receive function"""
    source = """
    class Wallet {
        payable method receive() {
            var x: uint256 := 1;
        }
    }
    """
    parser = DafnyParser(source)
    contract = parser.parse()
    
    assert contract.receive_method is not None
    assert contract.receive_method.name == "receive"
    assert len(contract.methods) == 0  # receive not in regular methods

def test_fallback_function_parsing():
    """Test parsing fallback function"""
    source = """
    class Wallet {
        method fallback() {
            var x: uint256 := 1;
        }
    }
    """
    parser = DafnyParser(source)
    contract = parser.parse()
    
    assert contract.fallback_method is not None
    assert contract.fallback_method.name == "fallback"
    assert len(contract.methods) == 0  # fallback not in regular methods

def test_indexed_event_generation():
    """Test Yul generation for indexed events"""
    source = """
    class Token {
        event Transfer(address indexed from, address indexed to, uint256 amount)
        
        method transfer(from: address, to: address, amount: uint256) {
            emit Transfer(from, to, amount);
        }
    }
    """
    parser = DafnyParser(source)
    contract = parser.parse()
    generator = YulGenerator()
    yul = generator.generate(contract)
    
    # Should use log3 (sig + 2 indexed params)
    assert "log3" in yul

def test_custom_error_generation():
    """Test Yul generation for custom errors"""
    source = """
    class Token {
        error InsufficientBalance(uint256 requested, uint256 available)
        
        method transfer(amount: uint256) {
            revert InsufficientBalance(amount, 100);
        }
    }
    """
    parser = DafnyParser(source)
    contract = parser.parse()
    generator = YulGenerator()
    yul = generator.generate(contract)
    
    # Should compute error selector and revert
    assert "revert" in yul

def test_selfdestruct_generation():
    """Test Yul generation for selfdestruct"""
    source = """
    class Token {
        method destroy(recipient: address) {
            selfdestruct(recipient);
        }
    }
    """
    parser = DafnyParser(source)
    contract = parser.parse()
    generator = YulGenerator()
    yul = generator.generate(contract)
    
    assert "selfdestruct" in yul

def test_receive_function_generation():
    """Test Yul generation for receive function"""
    source = """
    class Wallet {
        var balance: uint256
        
        payable method receive() {
            balance := balance + 1;
        }
    }
    """
    parser = DafnyParser(source)
    contract = parser.parse()
    generator = YulGenerator()
    yul = generator.generate(contract)
    
    # Should check for no calldata and has value
    assert "receive_fn" in yul
    assert "calldatasize" in yul

def test_fallback_function_generation():
    """Test Yul generation for fallback function"""
    source = """
    class Wallet {
        var balance: uint256
        
        method fallback() {
            balance := balance + 1;
        }
    }
    """
    parser = DafnyParser(source)
    contract = parser.parse()
    generator = YulGenerator()
    yul = generator.generate(contract)
    
    # Should call fallback_fn instead of revert
    assert "fallback_fn" in yul

def test_complete_example():
    """Test complete example with all Phase 6 features"""
    source = """
    class Vault {
        var balance: uint256
        var owner: address
        
        event Deposit(address indexed user, uint256 amount)
        event Withdrawal(address indexed user, uint256 amount)
        
        error Unauthorized(address caller)
        error InsufficientBalance(uint256 requested, uint256 available)
        
        payable method receive() {
            balance := balance + msg.value;
            emit Deposit(msg.sender, msg.value);
        }
        
        method withdraw(amount: uint256) {
            if (msg.sender != owner) {
                revert Unauthorized(msg.sender);
            }
            if (amount > balance) {
                revert InsufficientBalance(amount, balance);
            }
            balance := balance - amount;
            emit Withdrawal(msg.sender, amount);
        }
        
        method destroy() {
            if (msg.sender != owner) {
                revert Unauthorized(msg.sender);
            }
            selfdestruct(owner);
        }
    }
    """
    parser = DafnyParser(source)
    contract = parser.parse()
    
    # Check parsing
    assert len(contract.events) == 2
    assert len(contract.errors) == 2
    assert contract.receive_method is not None
    assert len(contract.methods) == 2
    
    # Check generation
    generator = YulGenerator()
    yul = generator.generate(contract)
    
    assert "receive_fn" in yul
    assert "log2" in yul  # Indexed events
    assert "selfdestruct" in yul
    assert "revert" in yul
