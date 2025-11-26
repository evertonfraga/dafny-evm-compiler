class VerifiedTokenSimple {
  var totalSupply: uint256
  var balance: uint256

  constructor()
    modifies this
    ensures totalSupply == 1000000
    ensures balance == 0
  {
    totalSupply := 1000000;
    balance := 0;
  }

  method mint(amount: uint256)
    requires amount > 0
    requires totalSupply + amount <= 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
    modifies this
    ensures totalSupply == old(totalSupply) + amount
    ensures balance == old(balance) + amount
  {
    totalSupply := totalSupply + amount;
    balance := balance + amount;
  }

  method getBalance() returns (bal: uint256)
    ensures bal == balance
  {
    return balance;
  }

  method getTotalSupply() returns (supply: uint256)
    ensures supply == totalSupply
  {
    return totalSupply;
  }
}
