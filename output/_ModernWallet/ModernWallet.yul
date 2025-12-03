object "ModernWallet" {
  code {
    sstore(0, 0)
    sstore(1, 0)
    sstore(2, 0)
    sstore(3, 0)
    sstore(4, 0)
    datacopy(0, dataoffset("runtime"), datasize("runtime"))
    return(0, datasize("runtime"))
  }
  object "runtime" {
    code {
      let selector := shr(224, calldataload(0))
      if eq(selector, 0x90fa17bb) {
        constructor()
      }
      if eq(selector, 0xd0e30db0) {
        deposit()
      }
      if eq(selector, 0x2e1a7d4d) {
        withdraw()
      }
      if eq(selector, 0x310ec4a7) {
        setAllowance()
      }
      if eq(selector, 0xc8c4d013) {
        withdrawWithAllowance()
      }
      if eq(selector, 0x12065fe0) {
        getBalance()
      }
      if eq(selector, 0x893d20e8) {
        getOwner()
      }
      if eq(selector, 0x4c89867f) {
        getLastUpdate()
      }
      if eq(selector, 0x8f32d59b) {
        isOwner()
      }
      if eq(selector, 0xc1625292) {
        batchProcess()
      }
      if eq(selector, 0x0f67f3d3) {
        processRange()
      }
      revert(0, 0)

      function keccak256_mapping(slot, key) -> result {
        mstore(0, slot)
        mstore(32, key)
        result := keccak256(0, 64)
      }

      function keccak256_hash(value) -> result {
        mstore(0, value)
        result := keccak256(0, 32)
      }

      function keccak256_single(slot) -> result {
        mstore(0, slot)
        result := keccak256(0, 32)
      }

      function constructor() {
        if callvalue() { revert(0, 0) }
    sstore(0, caller())
    sstore(1, 0)
    sstore(3, 0)
    sstore(2, timestamp())
    return(0, 0)
      }

      function deposit() {
        let success := 0
        if iszero(gt(callvalue(), 0)) { revert(0, 0) }
    sstore(1, add(sload(1), callvalue()))
    sstore(2, timestamp())
    sstore(3, add(sload(3), 1))
    mstore(0, caller())
    mstore(32, callvalue())
    mstore(64, timestamp())
    log1(0, 96, 0x90890809c654f11d6e72a28fa60149770a0d11ec6c92319d6ceb2bb0a4ea1a15)
    mstore(0, true)
    return(0, 32)
      }

      function withdraw() {
        if callvalue() { revert(0, 0) }
        let amount := calldataload(4)
        let success := 0
        if iszero(gt(amount, 0)) { revert(0, 0) }
        if iszero(iszero(gt(amount, sload(1)))) { revert(0, 0) }
    if eq(caller(), sload(0)) {
      sstore(1, sub(sload(1), amount))
      sstore(2, timestamp())
      sstore(3, add(sload(3), 1))
      mstore(0, caller())
      mstore(32, amount)
      log1(0, 64, 0x7fcf532c15f0a6db0bd6d0e038bea71d30d808c7d98cb3bf7268a95bf5081b65)
      mstore(0, true)
      return(0, 32)
    }
    mstore(0, 0)
    return(0, 32)
      }

      function setAllowance() {
        if callvalue() { revert(0, 0) }
        let spender := calldataload(4)
        let amount := calldataload(36)
        if iszero(eq(caller(), sload(0))) { revert(0, 0) }
    sstore(keccak256_mapping(4, spender), amount)
    mstore(0, spender)
    mstore(32, amount)
    log1(0, 64, 0xfe8c0d8594f34b56806542999bd528bee3ffe8a95e165d8e5c104f0b97cf8962)
    return(0, 0)
      }

      function withdrawWithAllowance() {
        if callvalue() { revert(0, 0) }
        let amount := calldataload(4)
        let success := 0
        if iszero(gt(amount, 0)) { revert(0, 0) }
    let allowed := sload(keccak256_mapping(4, caller()))
    if iszero(lt(allowed, amount)) {
      sstore(1, sub(sload(1), amount))
      sstore(keccak256_mapping(4, caller()), sub(allowed, amount))
      mstore(0, caller())
      mstore(32, amount)
      log1(0, 64, 0x7fcf532c15f0a6db0bd6d0e038bea71d30d808c7d98cb3bf7268a95bf5081b65)
      mstore(0, true)
      return(0, 32)
    }
    mstore(0, 0)
    return(0, 32)
      }

      function getBalance() {
        if callvalue() { revert(0, 0) }
        let bal := 0
    mstore(0, sload(1))
    return(0, 32)
      }

      function getOwner() {
        if callvalue() { revert(0, 0) }
        let addr := 0
    mstore(0, sload(0))
    return(0, 32)
      }

      function getLastUpdate() {
        if callvalue() { revert(0, 0) }
        let fn_timestamp := 0
    mstore(0, sload(2))
    return(0, 32)
      }

      function isOwner() {
        if callvalue() { revert(0, 0) }
        let result := 0
    if eq(caller(), sload(0)) {
      mstore(0, true)
      return(0, 32)
    }
    mstore(0, false)
    return(0, 32)
      }

      function batchProcess() {
        if callvalue() { revert(0, 0) }
        let count := calldataload(4)
    let i := 0
    for { } lt(i, count) { } {
      sstore(3, add(sload(3), 1))
      i := add(i, 1)
    }
    return(0, 0)
      }

      function processRange() {
        if callvalue() { revert(0, 0) }
        let start := calldataload(4)
        let end := calldataload(36)
    for { let i := start } lt(i, end) { i := add(i, 1) } {
      sstore(3, add(sload(3), 1))
    }
    return(0, 0)
      }

    }
  }
}
