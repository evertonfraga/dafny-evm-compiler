class SimpleTokenNoConstructor {
  public var totalSupply: uint256
  public var balances: mapping<address, uint256>

  constructor()
    modifies this
  {
    totalSupply := 1000000;
    balances := balances[msg.sender := 1000000];
  }

  method mint(amount: uint256)
    requires amount > 0
    modifies this
  {
    totalSupply := totalSupply + amount;
    balances[msg.sender] := balances[msg.sender] + amount;
  }

  method burn(amount: uint256)
    requires amount > 0
    requires balances[msg.sender] >= amount
    modifies this
  {
    balances[msg.sender] := balances[msg.sender] - amount;
    totalSupply := totalSupply - amount;
  }
}
