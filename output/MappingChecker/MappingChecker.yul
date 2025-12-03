object "MappingChecker" {
  code {
    sstore(0, 0)
    datacopy(0, dataoffset("runtime"), datasize("runtime"))
    return(0, datasize("runtime"))
  }
  object "runtime" {
    code {
      let selector := shr(224, calldataload(0))
      if eq(selector, 0x22b2678a) {
        hasBalance()
      }
      if eq(selector, 0xe30443bc) {
        setBalance()
      }
      if eq(selector, 0x3c7371eb) {
        checkAndGet()
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

      function hasBalance() {
        if callvalue() { revert(0, 0) }
        let addr := calldataload(4)
        let exists := 0
    exists := iszero(iszero(sload(keccak256_mapping(0, addr))))
    mstore(0, exists)
    return(0, 32)
      }

      function setBalance() {
        if callvalue() { revert(0, 0) }
        let addr := calldataload(4)
        let amount := calldataload(36)
        if iszero(gt(amount, 0)) { revert(0, 0) }
    sstore(keccak256_mapping(0, addr), amount)
    return(0, 0)
      }

      function checkAndGet() {
        if callvalue() { revert(0, 0) }
        let addr := calldataload(4)
        let has := 0
        let value := 0
    has := iszero(iszero(sload(keccak256_mapping(0, addr))))
    value := sload(keccak256_mapping(0, addr))
    mstore(0, has)
    mstore(32, value)
    return(0, 64)
      }

    }
  }
}
