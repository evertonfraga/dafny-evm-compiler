object "Counter" {
  code {
    sstore(0, 0)
    sstore(1, 0)
    sstore(0, 0)
    sstore(1, 1000)
    datacopy(0, dataoffset("runtime"), datasize("runtime"))
    return(0, datasize("runtime"))
  }
  object "runtime" {
    code {
      let selector := shr(224, calldataload(0))
      if eq(selector, 0xd09de08a) {
        increment()
      }
      if eq(selector, 0x2baeceb7) {
        decrement()
      }
      if eq(selector, 0xd826f88f) {
        reset()
      }
      if eq(selector, 0xa87d942c) {
        getCount()
      }
      if eq(selector, 0x9984f30d) {
        setMaxValue()
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

      function increment() {
        if callvalue() { revert(0, 0) }
        let newCount := 0
        if iszero(lt(sload(0), sload(1))) { revert(0, 0) }
    sstore(0, add(sload(0), 1))
    mstore(0, sload(0))
    return(0, 32)
      }

      function decrement() {
        if callvalue() { revert(0, 0) }
        let newCount := 0
        if iszero(gt(sload(0), 0)) { revert(0, 0) }
    sstore(0, sub(sload(0), 1))
    mstore(0, sload(0))
    return(0, 32)
      }

      function reset() {
        if callvalue() { revert(0, 0) }
    sstore(0, 0)
    return(0, 0)
      }

      function getCount() {
        if callvalue() { revert(0, 0) }
        let value := 0
    mstore(0, sload(0))
    return(0, 32)
      }

      function setMaxValue() {
        if callvalue() { revert(0, 0) }
        let newMax := calldataload(4)
        if iszero(iszero(lt(newMax, sload(0)))) { revert(0, 0) }
    sstore(1, newMax)
    return(0, 0)
      }

    }
  }
}
