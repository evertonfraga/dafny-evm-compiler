object "Math" {
  code {
    sstore(0, 0)
    sstore(1, 0)
    sstore(0, 10)
    sstore(1, 20)
    datacopy(0, dataoffset("runtime"), datasize("runtime"))
    return(0, datasize("runtime"))
  }
  object "runtime" {
    code {
      let selector := shr(224, calldataload(0))
      if eq(selector, 0x19eb4a90) {
        getValues()
      }
      if eq(selector, 0x6355ade7) {
        divMod()
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

      function getValues() {
        if callvalue() { revert(0, 0) }
        let a := 0
        let b := 0
    mstore(0, sload(0))
    mstore(32, sload(1))
    return(0, 64)
      }

      function divMod() {
        if callvalue() { revert(0, 0) }
        let dividend := calldataload(4)
        let divisor := calldataload(36)
        let quotient := 0
        let remainder := 0
        if iszero(gt(divisor, 0)) { revert(0, 0) }
    mstore(0, div(dividend, divisor))
    mstore(32, mod(dividend, divisor))
    return(0, 64)
      }

    }
  }
}
