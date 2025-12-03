object "ERC20Verified" {
  code {
    function keccak256_mapping(slot, key) -> result {
      mstore(0, slot)
      mstore(32, key)
      result := keccak256(0, 64)
    }

    sstore(0, 0)
    sstore(1, 0)
    sstore(2, 0)
    sstore(3, 0)
    sstore(4, 0)
    let initialSupply := calldataload(0)
    sstore(0, initialSupply)
    sstore(1, caller())
    sstore(2, false)
    sstore(keccak256_mapping(3, caller()), initialSupply)
    datacopy(0, dataoffset("runtime"), datasize("runtime"))
    return(0, datasize("runtime"))
  }
  object "runtime" {
    code {
      let selector := shr(224, calldataload(0))
      if eq(selector, 0xa9059cbb) {
        transfer()
      }
      if eq(selector, 0x095ea7b3) {
        approve()
      }
      if eq(selector, 0x23b872dd) {
        transferFrom()
      }
      if eq(selector, 0x40c10f19) {
        mint()
      }
      if eq(selector, 0x9dc29fac) {
        burn()
      }
      if eq(selector, 0x8456cb59) {
        pause()
      }
      if eq(selector, 0x3f4ba83a) {
        unpause()
      }
      if eq(selector, 0x70a08231) {
        balanceOf()
      }
      if eq(selector, 0xdd62ed3e) {
        allowance()
      }
      if eq(selector, 0xc4e41b22) {
        getTotalSupply()
      }
      if eq(selector, 0x893d20e8) {
        getOwner()
      }
      if eq(selector, 0xb187bd26) {
        isPaused()
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
        let to := calldataload(4)
        let amount := calldataload(36)
        let success := 0
        if iszero(gt(amount, 0)) { revert(0, 0) }
        if iszero(iszero(eq(to, 0))) { revert(0, 0) }
        if iszero(iszero(lt(sload(keccak256_mapping(3, caller())), amount))) { revert(0, 0) }
        if iszero(eq(sload(2), false)) { revert(0, 0) }
    sstore(keccak256_mapping(3, caller()), sub(sload(keccak256_mapping(3, caller())), amount))
    sstore(keccak256_mapping(3, to), add(sload(keccak256_mapping(3, to)), amount))
    mstore(0, true)
    return(0, 32)
      }

      function approve() {
        if callvalue() { revert(0, 0) }
        let spender := calldataload(4)
        let amount := calldataload(36)
        let success := 0
        if iszero(iszero(eq(spender, 0))) { revert(0, 0) }
        if iszero(eq(sload(2), false)) { revert(0, 0) }
    sstore(keccak256_mapping(keccak256_mapping(4, caller()), spender), amount)
    mstore(0, true)
    return(0, 32)
      }

      function transferFrom() {
        if callvalue() { revert(0, 0) }
        let from := calldataload(4)
        let to := calldataload(36)
        let amount := calldataload(68)
        let success := 0
        if iszero(gt(amount, 0)) { revert(0, 0) }
        if iszero(iszero(eq(to, 0))) { revert(0, 0) }
        if iszero(iszero(lt(sload(keccak256_mapping(3, from)), amount))) { revert(0, 0) }
        if iszero(iszero(lt(sload(keccak256_mapping(keccak256_mapping(4, from), caller())), amount))) { revert(0, 0) }
        if iszero(eq(sload(2), false)) { revert(0, 0) }
    sstore(keccak256_mapping(3, from), sub(sload(keccak256_mapping(3, from)), amount))
    sstore(keccak256_mapping(3, to), add(sload(keccak256_mapping(3, to)), amount))
    sstore(keccak256_mapping(keccak256_mapping(4, from), caller()), sub(sload(keccak256_mapping(keccak256_mapping(4, from), caller())), amount))
    mstore(0, true)
    return(0, 32)
      }

      function mint() {
        if callvalue() { revert(0, 0) }
        let to := calldataload(4)
        let amount := calldataload(36)
        let success := 0
        if iszero(gt(amount, 0)) { revert(0, 0) }
        if iszero(eq(caller(), sload(1))) { revert(0, 0) }
        if iszero(eq(sload(2), false)) { revert(0, 0) }
    sstore(0, add(sload(0), amount))
    sstore(keccak256_mapping(3, to), add(sload(keccak256_mapping(3, to)), amount))
    mstore(0, true)
    return(0, 32)
      }

      function burn() {
        if callvalue() { revert(0, 0) }
        let from := calldataload(4)
        let amount := calldataload(36)
        let success := 0
        if iszero(gt(amount, 0)) { revert(0, 0) }
        if iszero(eq(caller(), sload(1))) { revert(0, 0) }
        if iszero(iszero(gt(amount, sload(0)))) { revert(0, 0) }
        if iszero(iszero(gt(amount, sload(keccak256_mapping(3, from))))) { revert(0, 0) }
        if iszero(eq(sload(2), false)) { revert(0, 0) }
    sstore(0, sub(sload(0), amount))
    sstore(keccak256_mapping(3, from), sub(sload(keccak256_mapping(3, from)), amount))
    mstore(0, true)
    return(0, 32)
      }

      function pause() {
        if callvalue() { revert(0, 0) }
        if iszero(eq(caller(), sload(1))) { revert(0, 0) }
        if iszero(eq(sload(2), false)) { revert(0, 0) }
    sstore(2, true)
    return(0, 0)
      }

      function unpause() {
        if callvalue() { revert(0, 0) }
        if iszero(eq(caller(), sload(1))) { revert(0, 0) }
        if iszero(eq(sload(2), true)) { revert(0, 0) }
    sstore(2, false)
    return(0, 0)
      }

      function balanceOf() {
        if callvalue() { revert(0, 0) }
        let account := calldataload(4)
        let fn_balance := 0
    mstore(0, sload(keccak256_mapping(3, account)))
    return(0, 32)
      }

      function allowance() {
        if callvalue() { revert(0, 0) }
        let tokenOwner := calldataload(4)
        let spender := calldataload(36)
        let remaining := 0
    mstore(0, sload(keccak256_mapping(keccak256_mapping(4, tokenOwner), spender)))
    return(0, 32)
      }

      function getTotalSupply() {
        if callvalue() { revert(0, 0) }
        let supply := 0
    mstore(0, sload(0))
    return(0, 32)
      }

      function getOwner() {
        if callvalue() { revert(0, 0) }
        let ownerAddr := 0
    mstore(0, sload(1))
    return(0, 32)
      }

      function isPaused() {
        if callvalue() { revert(0, 0) }
        let status := 0
    mstore(0, sload(2))
    return(0, 32)
      }

    }
  }
}
