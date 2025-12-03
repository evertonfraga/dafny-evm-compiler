object "AccessControlled" {
  code {
    sstore(0, 0)
    sstore(1, 0)
    sstore(2, 0)
    sstore(0, caller())
    sstore(1, false)
    sstore(2, 0)
    datacopy(0, dataoffset("runtime"), datasize("runtime"))
    return(0, datasize("runtime"))
  }
  object "runtime" {
    code {
      let selector := shr(224, calldataload(0))
      if eq(selector, 0xf2fde38b) {
        transferOwnership()
      }
      if eq(selector, 0x8456cb59) {
        pause()
      }
      if eq(selector, 0x3f4ba83a) {
        unpause()
      }
      if eq(selector, 0xd0e30db0) {
        deposit()
      }
      if eq(selector, 0x2e1a7d4d) {
        withdraw()
      }
      if eq(selector, 0x12065fe0) {
        getBalance()
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

      function transferOwnership() {
        if callvalue() { revert(0, 0) }
        let newOwner := calldataload(4)
        if iszero(eq(caller(), sload(0))) { revert(0, 0) }
    let oldOwner := sload(0)
    sstore(0, newOwner)
    mstore(0, oldOwner)
    mstore(32, newOwner)
    log1(0, 64, 0x8be0079c531659141344cd1fd0a4f28419497f9722a3daafe3b4186f6b6457e0)
    return(0, 0)
      }

      function pause() {
        if callvalue() { revert(0, 0) }
        if iszero(eq(caller(), sload(0))) { revert(0, 0) }
        if iszero(iszero(sload(1))) { revert(0, 0) }
    sstore(1, true)
    log1(0, 0, 0x9e87fac88ff661f02d44f95383c817fece4bce600a3dab7a54406878b965e752)
    return(0, 0)
      }

      function unpause() {
        if callvalue() { revert(0, 0) }
        if iszero(eq(caller(), sload(0))) { revert(0, 0) }
        if iszero(sload(1)) { revert(0, 0) }
    sstore(1, false)
    log1(0, 0, 0xa45f47fdea8a1efdd9029a5691c7f759c32b7c698632b563573e155625d16933)
    return(0, 0)
      }

      function deposit() {
        if iszero(iszero(sload(1))) { revert(0, 0) }
    sstore(2, add(sload(2), callvalue()))
    return(0, 0)
      }

      function withdraw() {
        if callvalue() { revert(0, 0) }
        let amount := calldataload(4)
        if iszero(eq(caller(), sload(0))) { revert(0, 0) }
        if iszero(iszero(sload(1))) { revert(0, 0) }
        if iszero(iszero(gt(amount, sload(2)))) { revert(0, 0) }
    sstore(2, sub(sload(2), amount))
    return(0, 0)
      }

      function getBalance() {
        if callvalue() { revert(0, 0) }
        let b := 0
    mstore(0, sload(2))
    return(0, 32)
      }

    }
  }
}
