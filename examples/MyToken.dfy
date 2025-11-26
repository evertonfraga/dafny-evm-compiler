class MyToken {
  var totalSupply: uint256
  var balances: mapping<address, uint256>

  constructor()
    modifies this
    ensures totalSupply == 1000000
  {
    totalSupply := 1000000;
  }

  method mint(to: address, amount: uint256)
    requires amount > 0
    modifies this
    ensures totalSupply == old(totalSupply) + amount
  {
    totalSupply := totalSupply + amount;
    balances[to] := balances[to] + amount;
  }

  method balanceOf(account: address) returns (balance: uint256)
  {
    return balances[account];
  }
}
