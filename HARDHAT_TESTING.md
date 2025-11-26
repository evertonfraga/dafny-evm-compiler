# Hardhat Testing Guide

This guide explains how to test Dafny-compiled smart contracts using Hardhat.

## Quick Start

```bash
# 1. Compile a Dafny contract for Hardhat
python3 compile_for_hardhat.py examples/SimpleToken.dfy

# 2. Run Hardhat tests
cd hardhat-tests
npx hardhat test
```

## Architecture

```
Dafny Source → Compiler → Bytecode + ABI → Hardhat Artifact → Test Suite
```

### Components

1. **compile_for_hardhat.py**: Compiles Dafny to Hardhat-compatible artifacts
2. **hardhat-tests/**: Hardhat project with test suite
3. **contracts-out/**: Generated artifacts (bytecode + ABI)

## Compilation Script

The `compile_for_hardhat.py` script:

```python
# Compiles Dafny and generates Hardhat artifact
python3 compile_for_hardhat.py <dafny_file>
```

Output format:
```json
{
  "contractName": "SimpleToken",
  "abi": [...],
  "bytecode": "0x...",
  "deployedBytecode": "0x...",
  "linkReferences": {},
  "deployedLinkReferences": {}
}
```

## Writing Tests

### Basic Test Structure

```javascript
const { expect } = require("chai");
const { ethers } = require("hardhat");
const fs = require("fs");
const path = require("path");

describe("MyContract", function () {
  let contract;
  let owner;

  beforeEach(async function () {
    [owner] = await ethers.getSigners();

    // Load Dafny-compiled artifact
    const artifact = JSON.parse(
      fs.readFileSync("../contracts-out/MyContract.json", "utf8")
    );

    // Deploy
    const factory = new ethers.ContractFactory(
      artifact.abi,
      artifact.bytecode,
      owner
    );
    contract = await factory.deploy();
    await contract.deployed();
  });

  it("Should work", async function () {
    // Test your contract
    await contract.someMethod();
  });
});
```

### Testing Preconditions

Dafny preconditions become runtime checks:

```dafny
method transfer(amount: uint256) returns (success: bool)
  requires amount > 0
  requires amount <= balance
{
  // ...
}
```

Test that preconditions are enforced:

```javascript
it("Should revert on zero amount", async function () {
  await expect(contract.transfer(0)).to.be.reverted;
});

it("Should revert on insufficient balance", async function () {
  await expect(contract.transfer(1000000)).to.be.reverted;
});
```

### Gas Usage Testing

```javascript
it("Should report gas usage", async function () {
  const tx = await contract.mint(1000);
  const receipt = await tx.wait();
  console.log(`Gas used: ${receipt.gasUsed.toString()}`);
  expect(receipt.gasUsed.toNumber()).to.be.lessThan(100000);
});
```

## Example: Testing SimpleToken

```bash
# Compile
python3 compile_for_hardhat.py examples/SimpleToken.dfy

# Run tests
cd hardhat-tests
npx hardhat test test/SimpleToken.test.js
```

## Supported Features

The compiler generates ABI for:

- ✅ Methods (public functions)
- ✅ Parameters and return values
- ✅ State mutability (view, pure, payable)
- ✅ Events
- ✅ Constructor
- ✅ Multiple return values
- ✅ Complex types (structs, arrays, mappings)

## Workflow

### 1. Write Dafny Contract

```dafny
class Counter {
  var count: uint256

  constructor()
    ensures count == 0
  {
    count := 0;
  }

  method increment()
    modifies this
    ensures count == old(count) + 1
  {
    count := count + 1;
  }

  method getCount() returns (c: uint256)
    ensures c == count
  {
    return count;
  }
}
```

### 2. Compile for Hardhat

```bash
python3 compile_for_hardhat.py examples/Counter.dfy
```

Output:
```
✓ Generated artifact: hardhat-tests/contracts-out/Counter.json
✓ Contract: Counter
✓ Bytecode size: 145 bytes
✓ Functions: 2
```

### 3. Write Tests

```javascript
// hardhat-tests/test/Counter.test.js
describe("Counter", function () {
  let counter;

  beforeEach(async function () {
    const artifact = JSON.parse(
      fs.readFileSync("../contracts-out/Counter.json", "utf8")
    );
    const factory = new ethers.ContractFactory(
      artifact.abi,
      artifact.bytecode,
      (await ethers.getSigners())[0]
    );
    counter = await factory.deploy();
    await counter.deployed();
  });

  it("Should start at zero", async function () {
    expect(await counter.getCount()).to.equal(0);
  });

  it("Should increment", async function () {
    await counter.increment();
    expect(await counter.getCount()).to.equal(1);
  });
});
```

### 4. Run Tests

```bash
cd hardhat-tests
npx hardhat test
```

## Advanced Features

### Testing Multiple Contracts

```bash
# Compile all contracts
python3 compile_for_hardhat.py examples/SimpleToken.dfy
python3 compile_for_hardhat.py examples/Counter.dfy
python3 compile_for_hardhat.py examples/ERC20Token.dfy

# Run all tests
cd hardhat-tests
npx hardhat test
```

### Integration Tests

Test interactions between multiple Dafny-compiled contracts:

```javascript
it("Should interact with other contracts", async function () {
  const token = await deployContract("Token");
  const vault = await deployContract("Vault");
  
  await token.approve(vault.address, 1000);
  await vault.deposit(token.address, 1000);
});
```

### Formal Verification + Testing

Enable verification during compilation:

```python
# In compile_for_hardhat.py, change:
compiler = DafnyEVMCompiler(verify=True)  # Enable verification

# Then compile
result = compiler.compile_file(dafny_file, skip_verification=False)
```

This ensures contracts are formally verified before testing.

## Troubleshooting

### Contract Deployment Fails

- Check bytecode is valid: `cat contracts-out/MyContract.json | jq .bytecode`
- Verify ABI is correct: `cat contracts-out/MyContract.json | jq .abi`
- Check Dafny compilation: `python3 cli.py examples/MyContract.dfy`

### Method Calls Revert

- Dafny preconditions are enforced at runtime
- Check that test inputs satisfy preconditions
- Use `--skip-verification` if verification is failing

### ABI Mismatch

- Recompile contract: `python3 compile_for_hardhat.py <file>`
- Clear Hardhat cache: `cd hardhat-tests && npx hardhat clean`
- Restart Hardhat network

## Benefits

1. **Formal Verification**: Contracts are proven correct before testing
2. **Automated ABI Generation**: No manual ABI writing
3. **Standard Testing**: Use familiar Hardhat/Ethers.js patterns
4. **Gas Analysis**: Measure gas usage of verified contracts
5. **Integration Testing**: Test interactions between verified contracts

## Next Steps

- Add more test cases for edge conditions
- Test gas optimization strategies
- Create integration test suites
- Set up CI/CD with automated testing
- Deploy to testnets for live testing

## Resources

- [Hardhat Documentation](https://hardhat.org/docs)
- [Ethers.js Documentation](https://docs.ethers.org/)
- [Dafny Language Reference](https://dafny.org/)
- [Project README](README.md)
