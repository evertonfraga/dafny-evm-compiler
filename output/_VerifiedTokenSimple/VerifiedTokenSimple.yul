object "VerifiedTokenSimple" {
  code {
    sstore(0, 0)
    sstore(1, 0)
    sstore(0, 1000000)
    sstore(1, 0)
    datacopy(0, dataoffset("runtime"), datasize("runtime"))
    return(0, datasize("runtime"))
  }
  object "runtime" {
    code {
      let selector := shr(224, calldataload(0))
      if eq(selector, 0xa0712d68) {
        mint()
      }
      if eq(selector, 0x12065fe0) {
        getBalance()
      }
      if eq(selector, 0xc4e41b22) {
        getTotalSupply()
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
        if iszero(gt(amount, 0)) { revert(0, 0) }
        if iszero(iszero(gt(add(sload(0), amount), 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF))) { revert(0, 0) }
    sstore(0, add(sload(0), amount))
    sstore(1, add(sload(1), amount))
    return(0, 0)
      }

      function getBalance() {
        if callvalue() { revert(0, 0) }
        let bal := 0
    mstore(0, sload(1))
    return(0, 32)
      }

      function getTotalSupply() {
        if callvalue() { revert(0, 0) }
        let supply := 0
    mstore(0, sload(0))
    return(0, 32)
      }

    }
  }
}
