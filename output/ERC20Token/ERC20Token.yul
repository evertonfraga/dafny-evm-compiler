object "ERC20Token" {
  code {
    sstore(0, 0)
    sstore(1, 0)
    sstore(2, 0)
    let initialSupply := calldataload(0)
    sstore(0, initialSupply)
    sstore(1, 0)
    sstore(2, false)
    datacopy(0, dataoffset("runtime"), datasize("runtime"))
    return(0, datasize("runtime"))
  }
  object "runtime" {
    code {
      let selector := shr(224, calldataload(0))
      if eq(selector, 0xa0712d68) {
        mint()
      }
      if eq(selector, 0x42966c68) {
        burn()
      }
      if eq(selector, 0x8456cb59) {
        pause()
      }
      if eq(selector, 0x3f4ba83a) {
        unpause()
      }
      if eq(selector, 0xc4e41b22) {
        getTotalSupply()
      }
      if eq(selector, 0xb187bd26) {
        isPaused()
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

      function mint() {
        if callvalue() { revert(0, 0) }
        let amount := calldataload(4)
        let success := 0
        if iszero(gt(amount, 0)) { revert(0, 0) }
        if iszero(eq(sload(2), false)) { revert(0, 0) }
    sstore(0, add(sload(0), amount))
    mstore(0, true)
    return(0, 32)
      }

      function burn() {
        if callvalue() { revert(0, 0) }
        let amount := calldataload(4)
        let success := 0
        if iszero(gt(amount, 0)) { revert(0, 0) }
        if iszero(iszero(gt(amount, sload(0)))) { revert(0, 0) }
        if iszero(eq(sload(2), false)) { revert(0, 0) }
    sstore(0, sub(sload(0), amount))
    mstore(0, true)
    return(0, 32)
      }

      function pause() {
        if callvalue() { revert(0, 0) }
        if iszero(eq(sload(2), false)) { revert(0, 0) }
    sstore(2, true)
    return(0, 0)
      }

      function unpause() {
        if callvalue() { revert(0, 0) }
        if iszero(eq(sload(2), true)) { revert(0, 0) }
    sstore(2, false)
    return(0, 0)
      }

      function getTotalSupply() {
        if callvalue() { revert(0, 0) }
        let supply := 0
    mstore(0, sload(0))
    return(0, 32)
      }

      function isPaused() {
        if callvalue() { revert(0, 0) }
        let status := 0
    mstore(0, sload(2))
    return(0, 32)
      }

    }
  }
}
