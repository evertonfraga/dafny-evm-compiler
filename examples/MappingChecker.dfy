class MappingChecker {
  var balances: mapping<address, uint256>

  method hasBalance(addr: address) returns (exists: bool)
  {
    exists := addr in balances;
    return exists;
  }

  method setBalance(addr: address, amount: uint256)
    requires amount > 0
  {
    balances[addr] := amount;
  }

  method checkAndGet(addr: address) returns (has: bool, value: uint256)
  {
    has := addr in balances;
    value := balances[addr];
    return has, value;
  }
}
