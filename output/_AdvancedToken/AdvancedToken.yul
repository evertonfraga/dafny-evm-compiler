object "AdvancedToken" {
  code {
    sstore(0, 0)
    sstore(1, 0)
    sstore(2, 0)
    sstore(3, 0)
    sstore(4, 0)
    datacopy(0, dataoffset("runtime"), datasize("runtime"))
    return(0, datasize("runtime"))
  }
  object "runtime" {
    code {
      let selector := shr(224, calldataload(0))
      if eq(selector, 0x767b6190) {
        constructor()
      }
      if eq(selector, 0xa9059cbb) {
        transfer()
      }
      if eq(selector, 0x095ea7b3) {
        approve()
      }
      if eq(selector, 0x70a08231) {
        balanceOf()
      }
      if eq(selector, 0xd0e30db0) {
        deposit()
      }
      if eq(selector, 0xe8a96b46) {
        getHolder()
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

      function constructor() {
        if callvalue() { revert(0, 0) }
        let initialSupply := calldataload(4)
        if iszero(gt(initialSupply, 0)) { revert(0, 0) }
    sstore(3, initialSupply)
    sstore(keccak256_mapping(0, sload(4)), initialSupply)
    mstore(0, sload(4))
    mstore(32, sload(4))
    mstore(64, initialSupply)
    log1(0, 96, 0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef)
    return(0, 0)
      }

      function transfer() {
        if callvalue() { revert(0, 0) }
        let to := calldataload(4)
        let amount := calldataload(36)
        let success := 0
        if iszero(gt(amount, 0)) { revert(0, 0) }
        if iszero(iszero(lt(sload(keccak256_mapping(0, sload(4))), amount))) { revert(0, 0) }
    let senderBalance := sload(keccak256_mapping(0, sload(4)))
    sstore(keccak256_mapping(0, sload(4)), sub(senderBalance, amount))
    sstore(keccak256_mapping(0, to), add(sload(keccak256_mapping(0, to)), amount))
    mstore(0, sload(4))
    mstore(32, to)
    mstore(64, amount)
    log1(0, 96, 0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef)
    mstore(0, true)
    return(0, 32)
      }

      function approve() {
        if callvalue() { revert(0, 0) }
        let spender := calldataload(4)
        let amount := calldataload(36)
        let success := 0
        if iszero(gt(amount, 0)) { revert(0, 0) }
    sstore(keccak256_mapping(1, spender), amount)
    mstore(0, sload(4))
    mstore(32, spender)
    mstore(64, amount)
    log1(0, 96, 0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925)
    mstore(0, true)
    return(0, 32)
      }

      function balanceOf() {
        if callvalue() { revert(0, 0) }
        let account := calldataload(4)
        let fn_balance := 0
    mstore(0, sload(keccak256_mapping(0, account)))
    return(0, 32)
      }

      function deposit() {
        let success := 0
    sstore(keccak256_mapping(0, sload(4)), add(sload(keccak256_mapping(0, sload(4))), 1000))
    sstore(3, add(sload(3), 1000))
    mstore(0, sload(4))
    mstore(32, 1000)
    log1(0, 64, 0xe1fffcc4923d04b559f4d29a8bfc6cda04eb5b0d3c460751c2402c5c5cc9109c)
    mstore(0, true)
    return(0, 32)
      }

      function getHolder() {
        if callvalue() { revert(0, 0) }
        let index := calldataload(4)
        let holder := 0
        if iszero(lt(index, 100)) { revert(0, 0) }
    mstore(0, sload(keccak256_mapping(2, index)))
    return(0, 32)
      }

    }
  }
}
