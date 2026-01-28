class FullyVerifiedToken {
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
    requires totalSupply + amount <= 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
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

  method getTotalSupply() returns (supply: uint256)
    ensures supply == totalSupply
  {
    return totalSupply;
  }

  method transfer(sender: address, to: address, amount: uint256) returns (success: bool)
    requires amount > 0
    requires balances[sender] >= amount
    modifies this
  {
    balances[sender] := balances[sender] - amount;
    balances[to] := balances[to] + amount;
    return true;
  }
}
