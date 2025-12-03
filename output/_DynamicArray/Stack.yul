object "Stack" {
  code {
    sstore(0, 0)
    datacopy(0, dataoffset("runtime"), datasize("runtime"))
    return(0, datasize("runtime"))
  }
  object "runtime" {
    code {
      let selector := shr(224, calldataload(0))
      if eq(selector, 0x959ac484) {
        push()
      }
      if eq(selector, 0xa4ece52c) {
        fn_pop()
      }
      if eq(selector, 0x949d225d) {
        size()
      }
      if eq(selector, 0x9507d39a) {
        get()
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

      function push() {
        if callvalue() { revert(0, 0) }
        let value := calldataload(4)
    let len := sload(0)
    sstore(add(keccak256_single(0), len), value)
    sstore(0, add(len, 1))
    return(0, 0)
      }

      function fn_pop() {
        if callvalue() { revert(0, 0) }
    let len := sload(0)
    if iszero(len) { revert(0, 0) }
    let newLen := sub(len, 1)
    sstore(add(keccak256_single(0), newLen), 0)
    sstore(0, newLen)
    return(0, 0)
      }

      function size() {
        if callvalue() { revert(0, 0) }
        let len := 0
    mstore(0, sload(0))
    return(0, 32)
      }

      function get() {
        if callvalue() { revert(0, 0) }
        let index := calldataload(4)
        let value := 0
    mstore(0, sload(keccak256_mapping(0, index)))
    return(0, 32)
      }

    }
  }
}
