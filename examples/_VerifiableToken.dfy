include "../src/dafny_prelude.dfy"

class VerifiableToken {
  var totalSupply: uint256
  var balances: uint256

  constructor()
    ensures totalSupply == 1000000
    ensures balances == 0
  {
    totalSupply := 1000000;
    balances := 0;
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

  method balanceOf() returns (balance: uint256)
    ensures balance == balances
  {
    return balances;
  }

  method getTotalSupply() returns (supply: uint256)
    ensures supply == totalSupply
  {
    return totalSupply;
  }
}
