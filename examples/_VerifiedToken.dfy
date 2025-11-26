class VerifiedToken {
  var totalSupply: uint256
  var balance: uint256

  predicate Valid()
    reads this
  {
    totalSupply >= 0 && balance >= 0 && balance <= totalSupply
  }

  constructor()
    ensures totalSupply == 1000000
    ensures balance == 1000000
    ensures Valid()
  {
    totalSupply := 1000000;
    balance := 1000000;
  }

  method transfer(amount: uint256) returns (success: bool)
    requires Valid()
    requires amount > 0
    requires amount <= balance
    modifies this
    ensures Valid()
    ensures balance == old(balance) - amount
    ensures success == true
  {
    balance := balance - amount;
    return true;
  }

  method getBalance() returns (bal: uint256)
    requires Valid()
    ensures bal == balance
  {
    return balance;
  }
}
