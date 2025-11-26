# ERC20 Token Comprehensive Verification Plan

## Current State Analysis

### Existing Features
- ✅ Basic totalSupply tracking
- ✅ Pause/unpause mechanism
- ✅ Mint/burn operations
- ✅ Owner field (unused)

### Missing Critical ERC20 Features
- ❌ Per-address balances (mapping)
- ❌ Transfer functionality
- ❌ Allowances (approve/transferFrom)
- ❌ Events (Transfer, Approval)
- ❌ Owner authorization checks

## Verification Opportunities

### 1. **Invariants** (Contract-level properties that always hold)

#### Current
```dafny
invariant totalSupply >= 0
invariant paused == true || paused == false  // Redundant
```

#### Proposed
```dafny
// Core invariants
invariant totalSupply >= 0
invariant totalSupply <= MAX_UINT256

// Balance invariant: sum of all balances equals totalSupply
invariant forall addr :: balances[addr] >= 0
invariant (forall addr :: balances[addr]) <= totalSupply  // Simplified sum check

// Owner invariant
invariant owner != 0  // Owner must be set

// Pause state is boolean (already guaranteed by type)
```

### 2. **Preconditions** (Requirements before method execution)

#### Mint
```dafny
requires amount > 0
requires paused == false
requires msg.sender == owner  // Only owner can mint
requires totalSupply + amount <= MAX_UINT256  // Overflow protection
```

#### Burn
```dafny
requires amount > 0
requires amount <= totalSupply
requires paused == false
requires msg.sender == owner || balances[msg.sender] >= amount  // Owner or self-burn
```

#### Transfer
```dafny
requires amount > 0
requires balances[msg.sender] >= amount  // Sufficient balance
requires to != 0  // No burn via transfer
requires paused == false
```

#### Approve
```dafny
requires spender != 0
requires paused == false
```

#### TransferFrom
```dafny
requires amount > 0
requires balances[from] >= amount
requires allowances[from][msg.sender] >= amount
requires to != 0
requires paused == false
```

#### Pause/Unpause
```dafny
requires msg.sender == owner  // Only owner can pause
```

### 3. **Postconditions** (Guarantees after method execution)

#### Mint
```dafny
ensures totalSupply == old(totalSupply) + amount
ensures balances[to] == old(balances[to]) + amount
ensures forall addr :: addr != to ==> balances[addr] == old(balances[addr])
ensures success == true
```

#### Burn
```dafny
ensures totalSupply == old(totalSupply) - amount
ensures balances[from] == old(balances[from]) - amount
ensures forall addr :: addr != from ==> balances[addr] == old(balances[addr])
ensures success == true
```

#### Transfer
```dafny
ensures balances[msg.sender] == old(balances[msg.sender]) - amount
ensures balances[to] == old(balances[to]) + amount
ensures forall addr :: addr != msg.sender && addr != to ==> balances[addr] == old(balances[addr])
ensures success == true
```

#### Approve
```dafny
ensures allowances[msg.sender][spender] == amount
ensures forall owner, spender :: 
  (owner != msg.sender || spender != spender) ==> 
  allowances[owner][spender] == old(allowances[owner][spender])
ensures success == true
```

#### TransferFrom
```dafny
ensures balances[from] == old(balances[from]) - amount
ensures balances[to] == old(balances[to]) + amount
ensures allowances[from][msg.sender] == old(allowances[from][msg.sender]) - amount
ensures forall addr :: addr != from && addr != to ==> balances[addr] == old(balances[addr])
ensures success == true
```

### 4. **Safety Properties** (Things that should never happen)

```dafny
// No balance can exceed totalSupply
lemma BalanceNeverExceedsTotalSupply(addr: address)
  ensures balances[addr] <= totalSupply

// Total supply never decreases except via burn
lemma TotalSupplyMonotonic()
  ensures forall method :: method != burn ==> totalSupply >= old(totalSupply)

// Transfers are zero-sum
lemma TransferZeroSum(from: address, to: address, amount: uint256)
  requires balances[from] >= amount
  ensures balances[from] + balances[to] == old(balances[from]) + old(balances[to])

// No tokens created or destroyed in transfer
lemma TransferConservation()
  ensures totalSupply == old(totalSupply)

// Paused state prevents all state changes except unpause
lemma PausedPreventsOperations()
  requires paused == true
  ensures forall method :: method != unpause ==> totalSupply == old(totalSupply)
```

### 5. **Liveness Properties** (Things that should eventually happen)

```dafny
// Owner can always unpause if paused
ensures paused == true ==> (exists unpause_call :: eventually paused == false)

// Sufficient balance allows transfer
ensures balances[addr] >= amount ==> (exists transfer_call :: eventually success == true)
```

### 6. **Authorization Properties**

```dafny
// Only owner can mint
ensures mint_success ==> msg.sender == owner

// Only owner can pause/unpause
ensures pause_success ==> msg.sender == owner
ensures unpause_success ==> msg.sender == owner

// Anyone can transfer their own tokens
ensures transfer_success ==> balances[msg.sender] >= amount

// TransferFrom requires allowance
ensures transferFrom_success ==> allowances[from][msg.sender] >= amount
```

### 7. **Overflow/Underflow Protection**

```dafny
// Mint overflow check
requires totalSupply + amount <= MAX_UINT256
requires balances[to] + amount <= MAX_UINT256

// Burn underflow check
requires amount <= totalSupply
requires amount <= balances[from]

// Transfer underflow check
requires amount <= balances[from]

// Allowance underflow check
requires amount <= allowances[from][msg.sender]
```

## Implementation Phases

### Phase 1: Add Missing State Variables
```dafny
var balances: mapping<address, uint256>
var allowances: mapping<address, mapping<address, uint256>>
const MAX_UINT256: uint256 := 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
```

### Phase 2: Add Core Transfer Logic
- Implement `transfer(to: address, amount: uint256)`
- Add preconditions and postconditions
- Verify balance conservation

### Phase 3: Add Allowance System
- Implement `approve(spender: address, amount: uint256)`
- Implement `transferFrom(from: address, to: address, amount: uint256)`
- Implement `allowance(owner: address, spender: address)`

### Phase 4: Add Authorization
- Initialize owner in constructor with `msg.sender`
- Add owner checks to mint/burn/pause/unpause
- Add `onlyOwner` modifier pattern

### Phase 5: Add Events
```dafny
event Transfer(from: address, to: address, value: uint256)
event Approval(owner: address, spender: address, value: uint256)
event Paused(account: address)
event Unpaused(account: address)
```

### Phase 6: Add View Functions
```dafny
method balanceOf(account: address) returns (balance: uint256)
method allowance(owner: address, spender: address) returns (remaining: uint256)
```

### Phase 7: Strengthen Invariants
- Add sum-of-balances invariant
- Add allowance consistency checks
- Verify all invariants hold across all methods

### Phase 8: Add Lemmas and Proofs
- Prove conservation properties
- Prove authorization properties
- Prove safety properties

## Testing Strategy

### Unit Tests (Hardhat)
1. Deploy with initial supply
2. Test mint (owner only)
3. Test burn (owner only)
4. Test transfer (balance checks)
5. Test approve/transferFrom flow
6. Test pause/unpause (owner only)
7. Test overflow protection
8. Test zero-address protection
9. Test event emissions

### Formal Verification Tests
1. Verify all invariants hold
2. Verify all preconditions are sufficient
3. Verify all postconditions are achieved
4. Verify no arithmetic overflows
5. Verify authorization checks

## Success Criteria

- ✅ All methods have complete preconditions
- ✅ All methods have complete postconditions
- ✅ All invariants verified by Dafny
- ✅ All safety properties proven
- ✅ All Hardhat tests passing
- ✅ Full ERC20 compliance
- ✅ Gas-efficient implementation
- ✅ No compiler warnings

## Estimated Complexity

- **Lines of Code**: ~200 (from current 65)
- **Verification Time**: ~5-10 seconds
- **Implementation Time**: 2-3 hours
- **Testing Time**: 1-2 hours
