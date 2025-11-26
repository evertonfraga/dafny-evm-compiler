# Dafny EVM Compiler

An experimental compiler that translates Dafny smart contracts to EVM bytecode. Explores the integration of formal verification with smart contract development.

**Status:** Experimental - Research prototype with core Solidity feature support

## Architecture

```
Dafny Source → Verifier (optional) → Parser → AST → Yul Generator → Yul IR → Solidity Compiler → EVM Bytecode + ABI
```

## Installation

```bash
pip install -r requirements.txt
```

Ensure `solc` is installed:
```bash
# Ubuntu/Debian
sudo add-apt-repository ppa:ethereum/ethereum
sudo apt-get update
sudo apt-get install solc

# macOS
brew install solidity
```

## Usage

Compile a Dafny contract:
```bash
python cli.py examples/SimpleToken.dfy
```

Generate Yul only:
```bash
python cli.py examples/SimpleToken.dfy --yul-only
```

## Dafny Subset for EVM

Supported features:
- Integer types (uint8-uint256, int8-int256)
- Boolean operations
- Address type
- Bytes types (bytes, bytes32)
- Structs (declaration and field access)
- Arrays (dynamic arrays with push/pop/length)
- Mappings (single and nested)
- Multiple return values
- State variables (mapped to storage)
- Methods with preconditions/postconditions
- Control flow (if/else, for, while loops)
- Global variables (msg.sender, msg.value, block.timestamp, etc.)
- Payable methods
- Events (declaration and emission)
- Custom modifiers (onlyOwner, whenNotPaused, etc.)
- Visibility modifiers (public, private, internal, external)
- State mutability (view, pure, payable)
- ABI generation (JSON ABI output)
- Assertions and requires
- Basic arithmetic operations including modulo (%)

Example:
```dafny
class Token {
  var balance: uint256
  
  method transfer(amount: uint256) returns (success: bool)
    requires amount > 0
    requires amount <= balance
    ensures balance == old(balance) - amount
  {
    balance := balance - amount;
    return true;
  }
}
```

## Security Features

- Formal verification at Dafny level
- Precondition enforcement via require statements
- Postcondition validation
- Overflow protection through bounded types
- Deterministic compilation

## Project Structure

```
dafny-evm-compiler/
├── src/
│   ├── parser/          # Dafny AST parser
│   ├── translator/      # Yul code generator
│   ├── compiler/        # EVM bytecode compiler
│   └── dafny_compiler.py
├── docs/
│   ├── sessions/        # Session notes: YYYY-MM-DD-HHMM-[session-name].md
│   ├── planning/        # Planning documents
│   └── verification/    # Verification-related documentation
├── examples/            # Example contracts
├── tests/              # Test suite
└── cli.py              # Command-line interface
```

**Documentation Naming Convention:**
- Session notes use format: `YYYY-MM-DD-HHMM-[session-name].md`
- Example: `2025-11-26-1905-nested-mappings.md`
- Time uses 24-hour format with hyphens (no colons for filesystem compatibility)

## Testing

```bash
python -m pytest tests/
```

## Roadmap

- [x] Basic Dafny → Yul translation
- [x] Storage variable support
- [x] Method dispatch
- [x] Precondition/postcondition enforcement
- [x] Arrays and mappings (including nested)
- [x] Events
- [x] Payable methods
- [x] Custom modifiers
- [x] Visibility modifiers
- [x] State mutability
- [x] ABI generation
- [x] Library imports (parsing only)
- [x] Basic inheritance support (parsing)
- [x] Interfaces (parsing)
- [x] Inter-contract calls (low-level: call, delegatecall, staticcall)
- [ ] Full inheritance with field/method merging
- [ ] High-level typed contract calls
- [ ] Gas optimization passes
- [ ] Formal verification of translator

