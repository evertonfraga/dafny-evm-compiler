object "MyToken" {
  code {
    sstore(0, 0)
    sstore(1, 0)
    sstore(0, 1000000)
    datacopy(0, dataoffset("runtime"), datasize("runtime"))
    return(0, datasize("runtime"))
  }
  object "runtime" {
    code {
      let selector := shr(224, calldataload(0))
      if eq(selector, 0x40c10f19) {
        mint()
      }
      if eq(selector, 0x70a08231) {
        balanceOf()
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
        let to := calldataload(4)
        let amount := calldataload(36)
        if iszero(gt(amount, 0)) { revert(0, 0) }
    sstore(0, add(sload(0), amount))
    sstore(keccak256_mapping(1, to), add(sload(keccak256_mapping(1, to)), amount))
    return(0, 0)
      }

      function balanceOf() {
        if callvalue() { revert(0, 0) }
        let account := calldataload(4)
        let fn_balance := 0
    mstore(0, sload(keccak256_mapping(1, account)))
    return(0, 32)
      }

    }
  }
}
