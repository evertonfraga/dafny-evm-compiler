# Dafny EVM Compiler Test Suite

## Organization

Tests are organized into two main categories:

### 1. Verification Tests (`tests/verification/`)
Tests for Dafny's formal verification features applied to smart contracts.

- **test_preconditions.py** - requires clauses ✅ (4 tests)
- **test_postconditions.py** - ensures clauses (TODO)
- **test_invariants.py** - class and loop invariants (TODO)
- **test_assertions.py** - assert statements (TODO)
- **test_modifies_clause.py** - frame conditions (TODO)
- **test_ghost_code.py** - ghost variables and methods (TODO)
- **test_lemmas.py** - proof obligations (TODO)

### 2. Solidity Parity Tests (`tests/solidity_parity/`)
Tests for Solidity-compatible smart contract features.

- **test_events.py** - event declaration and emission (TODO)
- **test_modifiers.py** - custom modifiers (TODO)
- **test_visibility.py** - public/private/internal/external (TODO)
- **test_state_mutability.py** - view/pure/payable (TODO)
- **test_global_variables.py** - msg.sender, block.timestamp, etc. (TODO)
- **test_types.py** - uint256, address, bool, bytes (TODO)
- **test_mappings.py** - single and nested mappings (TODO)
- **test_arrays.py** - fixed and dynamic arrays (TODO)
- **test_structs.py** - struct declaration and usage (TODO)
- **test_control_flow.py** - if/else, for, while loops (TODO)
- **test_operators.py** - arithmetic, comparison, logical (TODO)
- **test_functions.py** - function declaration and calls (TODO)
- **test_constructors.py** - constructor with parameters (TODO)
- **test_inheritance.py** - contract inheritance (TODO)
- **test_interfaces.py** - interface declaration (TODO)
- **test_libraries.py** - library usage (TODO)
- **test_assembly.py** - inline assembly blocks (TODO)
- **test_unchecked.py** - unchecked arithmetic (TODO)
- **test_error_handling.py** - require/revert/custom errors (TODO)
- **test_special_functions.py** - receive/fallback/selfdestruct (TODO)
- **test_contract_calls.py** - external calls, delegatecall (TODO)
- **test_cryptographic.py** - keccak256, sha256, ecrecover (TODO)
- **test_abi_encoding.py** - abi.encode, abi.decode (TODO)
- **test_license.py** - SPDX license identifiers ✅ (5 tests)

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
python3 -m unittest discover tests/verification -v
python3 -m unittest discover tests/solidity_parity -v
```

Run specific test file:
```bash
python3 -m unittest tests.verification.test_preconditions -v
```

Run single test:
```bash
python3 -m unittest tests.verification.test_preconditions.TestPreconditions.test_simple_precondition -v
```

## Current Status

- **Total Tests**: 9 (4 verification + 5 solidity parity)
- **Passing**: 9
- **Coverage**: ~5% of planned tests

## Priority Implementation Order

### Phase 1: Core Verification (Week 1)
1. test_postconditions.py
2. test_invariants.py
3. test_modifies_clause.py

### Phase 2: Essential Solidity Features (Week 2)
1. test_events.py
2. test_modifiers.py
3. test_error_handling.py
4. test_constructors.py

### Phase 3: Data Types (Week 3)
1. test_types.py
2. test_mappings.py
3. test_arrays.py
4. test_structs.py

### Phase 4: Advanced Features (Week 4)
1. test_assembly.py
2. test_contract_calls.py
3. test_inheritance.py
4. test_interfaces.py

## Contributing

When adding new tests:
1. Follow the embedded code pattern
2. Add descriptive docstrings
3. Test both positive and negative cases
4. Update this README with test counts
5. Mark tests as ✅ when implemented
