# Foundry Integration Tests

Integration tests for Dafny-compiled smart contracts using Foundry.

## Setup

Foundry is installed at `~/.foundry/bin/`. Tests read compiled bytecode from `../../output/`.

## Running Tests

```bash
# Compile Dafny contracts first
cd ../..
python3 compile_for_foundry.py

# Run all tests
cd tests/foundry
forge test

# Run with verbosity
forge test -vv    # Show test results
forge test -vvv   # Show stack traces
forge test -vvvv  # Show full execution traces

# Run specific test
forge test --match-test testInitialValue

# Run specific contract
forge test --match-contract CounterTest

# Gas report
forge test --gas-report
```

## Test Structure

Tests deploy compiled Dafny contracts and verify their behavior:

1. **Read bytecode** - Load hex-encoded bytecode from `output/` directory
2. **Deploy contract** - Use `create` opcode to deploy with constructor
3. **Call methods** - Use low-level `call`/`staticcall` with ABI encoding
4. **Assert behavior** - Verify return values and state changes

## Current Tests

**Status: ✅ 11/11 tests passing**

### CounterTest (4 tests)
- ✅ `testInitialValue` - Verifies initial count is 0
- ✅ `testIncrement` - Increment works correctly
- ✅ `testMultipleIncrements` - Multiple increments work
- ✅ `testReset` - Reset works correctly

### SimpleTokenTest (4 tests)
- ✅ `testInitialBalance` - Initial balance is 0
- ✅ `testMint` - Minting increases balance
- ✅ `testTransferAfterMint` - Transfer works after minting
- ✅ `testTransferFailsWithoutBalance` - Transfer fails without balance

### MyTokenTest (3 tests)
- ✅ `testMintAndBalanceOf` - Mint and check balance
- ✅ `testMultipleMints` - Multiple mints to different addresses
- ✅ `testBalanceOfUnknownAddress` - Unknown address has 0 balance

## Key Findings

### Constructor Handling
Dafny constructors are compiled as regular methods that must be called after deployment:

```solidity
// Deploy
address deployed;
assembly {
    deployed := create(0, add(bytecode, 0x20), mload(bytecode))
}

// Call constructor method (if contract has one)
deployed.call(abi.encodeWithSignature("constructor()"));
```

Some contracts (like SimpleToken) execute constructor logic during deployment, while others (like Counter) expose it as a callable method.

### Precondition Enforcement
Methods with `requires` clauses properly revert when preconditions aren't met. Tests must satisfy preconditions or expect reverts.

## Next Steps

- [ ] Add ERC20Token tests
- [ ] Add property-based tests (fuzzing)
- [ ] Add gas benchmarking comparisons
- [ ] Test inter-contract calls
- [ ] Test events emission
- [ ] Test more complex contracts (ERC20Verified)
