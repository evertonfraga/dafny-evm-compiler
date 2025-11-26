# Dafny EVM Compiler Test Suite

## Organization

Tests are organized into three main categories:

### 1. Integration Tests (`tests/integration/`)
End-to-end tests for the complete compilation pipeline and verifier integration.

Tests include:
- Full compilation of example contracts
- Dafny verifier integration
- Contract structure validation
- Bytecode generation verification

### 2. Verification Tests (`tests/verification/`)
Tests for Dafny's formal verification features applied to smart contracts.

Coverage includes:
- Preconditions (requires clauses)
- Postconditions (ensures clauses)
- Class and loop invariants
- Assert statements
- Modifies clauses (frame conditions)
- Ghost variables and methods
- Lemmas and proof obligations

### 3. Solidity Parity Tests (`tests/solidity_parity/`)
Tests for Solidity-compatible smart contract features.

Coverage includes:
- Events (declaration, emission, indexing)
- Custom modifiers (onlyOwner, whenNotPaused, etc.)
- Global variables (msg.sender, msg.value, block.timestamp, etc.)
- Type system (uint, int, address, bool, bytes)
- Mappings (single and nested)
- Arrays (dynamic arrays with push/pop/length)
- Structs (declaration, access, nested)
- Control flow (if/else, for, while loops)
- Constructors (with/without parameters)
- ABI generation
- License identifiers (SPDX)

## Test Guidelines

### 1. Use Embedded Code Fragments
All tests use inline code strings, not external files:

```python
def test_feature(self):
    """Test description."""
    code = """
    class Contract {
      var state: uint256
      
      method doSomething()
        modifies this
      {
        state := 42;
      }
    }
    """
    result = self.compiler.compile(code, skip_verification=True)
    self.assertTrue(result['success'])
```

### 2. Test Structure
Each test file should:
- Import `DafnyEVMCompiler` from `src.dafny_compiler`
- Create compiler instance in `setUp()`
- Use descriptive test method names
- Include docstrings explaining what's tested
- Assert on compilation success and generated output

### 3. What to Test
- **Parsing**: Does the code parse correctly?
- **Compilation**: Does it compile to valid Yul/bytecode?
- **Output**: Does the generated code contain expected patterns?
- **ABI**: Is the ABI generated correctly?
- **Errors**: Do invalid inputs fail appropriately?

### 4. Running Tests

Run all tests:
```bash
python3 -m unittest discover tests -v
```

Run specific category:
```bash
python3 -m unittest discover tests/integration -v
python3 -m unittest discover tests/verification -v
python3 -m unittest discover tests/solidity_parity -v
```

Run specific test file:
```bash
python3 -m unittest tests.verification.test_preconditions -v
python3 -m unittest tests.integration.test_integration -v
```

Run single test:
```bash
python3 -m unittest tests.verification.test_preconditions.TestPreconditions.test_simple_precondition -v
```

## Contributing

When adding new tests:
1. Follow the embedded code pattern
2. Add descriptive docstrings
3. Test both positive and negative cases
4. Update this README with test counts
5. Mark tests as ✅ when implemented
