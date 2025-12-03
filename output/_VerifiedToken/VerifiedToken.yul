object "VerifiedToken" {
  code {
    sstore(0, 0)
    sstore(1, 0)
    sstore(0, 1000000)
    sstore(1, 1000000)
    datacopy(0, dataoffset("runtime"), datasize("runtime"))
    return(0, datasize("runtime"))
  }
  object "runtime" {
    code {
      let selector := shr(224, calldataload(0))
      if eq(selector, 0x12514bba) {
        transfer()
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

      function transfer() {
        if callvalue() { revert(0, 0) }
        let amount := calldataload(4)
        let success := 0
        if iszero(gt(amount, 0)) { revert(0, 0) }
        if iszero(iszero(gt(amount, sload(1)))) { revert(0, 0) }
    sstore(1, sub(sload(1), amount))
    mstore(0, true)
    return(0, 32)
      }

      function getBalance() {
        if callvalue() { revert(0, 0) }
        let bal := 0
    mstore(0, sload(1))
    return(0, 32)
      }

    }
  }
}
