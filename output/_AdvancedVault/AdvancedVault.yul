object "AdvancedVault" {
  code {
    sstore(0, 0)
    sstore(1, 0)
    sstore(2, 0)
    datacopy(0, dataoffset("runtime"), datasize("runtime"))
    return(0, datasize("runtime"))
  }
  object "runtime" {
    code {
      if and(iszero(calldatasize()), callvalue()) {
        receive_fn()
        return(0, 0)
      }
      let selector := shr(224, calldataload(0))
      if eq(selector, 0xd0e30db0) {
        deposit()
      }
      if eq(selector, 0x2e1a7d4d) {
        withdraw()
      }
      if eq(selector, 0xf2fde38b) {
        transferOwnership()
      }
      if eq(selector, 0x8456cb59) {
        pause()
      }
      if eq(selector, 0x3f4ba83a) {
        unpause()
      }
      if eq(selector, 0x12065fe0) {
        getBalance()
      }
      if eq(selector, 0x83197ef0) {
        destroy()
      }
      fallback_fn()

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

      function receive_fn() {
        sstore(0, add(sload(0), callvalue()))
        mstore(0, callvalue())
        log3(0, 32, 0x90890809c654f11d6e72a28fa60149770a0d11ec6c92319d6ceb2bb0a4ea1a15, caller(), timestamp())
      }

      function fallback_fn() {
        mstore(0, 0x08c379a000000000000000000000000000000000000000000000000000000000)
        revert(0, 4)
      }

      function deposit() {
    if sload(2) {
      mstore(0, 0xab35696f)
      revert(0, 4)
    }
    sstore(0, add(sload(0), callvalue()))
    mstore(0, callvalue())
    log3(0, 32, 0x90890809c654f11d6e72a28fa60149770a0d11ec6c92319d6ceb2bb0a4ea1a15, caller(), timestamp())
    return(0, 0)
      }

      function withdraw() {
        if callvalue() { revert(0, 0) }
        let amount := calldataload(4)
    if iszero(eq(caller(), sload(1))) {
      mstore(0, 0x8e4a23d6)
      mstore(4, caller())
      revert(0, 36)
    }
    if sload(2) {
      mstore(0, 0xab35696f)
      revert(0, 4)
    }
    if gt(amount, sload(0)) {
      mstore(0, 0xcf479181)
      mstore(4, amount)
      mstore(36, sload(0))
      revert(0, 68)
    }
    sstore(0, sub(sload(0), amount))
    mstore(0, amount)
    log2(0, 32, 0x7fcf532c15f0a6db0bd6d0e038bea71d30d808c7d98cb3bf7268a95bf5081b65, caller())
    return(0, 0)
      }

      function transferOwnership() {
        if callvalue() { revert(0, 0) }
        let newOwner := calldataload(4)
    if iszero(eq(caller(), sload(1))) {
      mstore(0, 0x8e4a23d6)
      mstore(4, caller())
      revert(0, 36)
    }
    if eq(newOwner, 0) {
      mstore(0, 0xd92e233d)
      revert(0, 4)
    }
    let oldOwner := sload(1)
    sstore(1, newOwner)
    log3(0, 0, 0x8be0079c531659141344cd1fd0a4f28419497f9722a3daafe3b4186f6b6457e0, oldOwner, newOwner)
    return(0, 0)
      }

      function pause() {
        if callvalue() { revert(0, 0) }
    if iszero(eq(caller(), sload(1))) {
      mstore(0, 0x8e4a23d6)
      mstore(4, caller())
      revert(0, 36)
    }
    sstore(2, true)
    log2(0, 0, 0x62e78cea01bee320cd4e420270b5ea74000d11b0c9f74754ebdbfc544b05a258, caller())
    return(0, 0)
      }

      function unpause() {
        if callvalue() { revert(0, 0) }
    if iszero(eq(caller(), sload(1))) {
      mstore(0, 0x8e4a23d6)
      mstore(4, caller())
      revert(0, 36)
    }
    sstore(2, false)
    log2(0, 0, 0x5db9ee0a495bf2e6ff9c91a7834c1ba4fdd244a5e8aa4e537bd38aeae4b073aa, caller())
    return(0, 0)
      }

      function getBalance() {
        if callvalue() { revert(0, 0) }
        let bal := 0
    mstore(0, sload(0))
    return(0, 32)
      }

      function destroy() {
        if callvalue() { revert(0, 0) }
    if iszero(eq(caller(), sload(1))) {
      mstore(0, 0x8e4a23d6)
      mstore(4, caller())
      revert(0, 36)
    }
    selfdestruct(sload(1))
    return(0, 0)
      }

    }
  }
}
