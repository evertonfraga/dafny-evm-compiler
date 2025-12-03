object "Registry" {
  code {
    sstore(0, 0)
    sstore(2, 0)
    sstore(2, 0)
    datacopy(0, dataoffset("runtime"), datasize("runtime"))
    return(0, datasize("runtime"))
  }
  object "runtime" {
    code {
      let selector := shr(224, calldataload(0))
      if eq(selector, 0xd5dcf127) {
        setAge()
      }
      if eq(selector, 0x967e6e65) {
        getAge()
      }
      if eq(selector, 0xd09de08a) {
        increment()
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

      function setAge() {
        if callvalue() { revert(0, 0) }
        let newAge := calldataload(4)
    sstore(0, newAge)
    return(0, 0)
      }

      function getAge() {
        if callvalue() { revert(0, 0) }
        let age := 0
    mstore(0, sload(0))
    return(0, 32)
      }

      function increment() {
        if callvalue() { revert(0, 0) }
    sstore(2, add(sload(2), 1))
    return(0, 0)
      }

    }
  }
}
