class SimpleToken {
  var totalSupply: uint256
  var balances: uint256

  constructor()
    ensures totalSupply == 1000000
  {
    totalSupply := 1000000;
  }

  method transfer(amount: uint256) returns (success: bool)
    requires amount > 0
    requires amount <= balances
    modifies this
    ensures balances == old(balances) - amount
  {
    var newBalance: uint256 := balances - amount;
    balances := newBalance;
    return true;
  }

  method getBalance() returns (balance: uint256)
    ensures balance == balances
  {
    return balances;
  }

  method mint(amount: uint256)
    requires amount > 0
    requires totalSupply + amount <= 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
    modifies this
    ensures totalSupply == old(totalSupply) + amount
    ensures balances == old(balances) + amount
  {
    totalSupply := totalSupply + amount;
    balances := balances + amount;
  }
}
