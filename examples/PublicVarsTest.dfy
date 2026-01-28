class PublicVarsTest {
  public var totalSupply: uint256
  public var balances: mapping<address, uint256>
  public var name: string

  constructor()
    modifies this
    ensures totalSupply == 1000000
  {
    totalSupply := 1000000;
    name := "Test Token";
  }

  method mint(to: address, amount: uint256)
    requires amount > 0
    modifies this
  {
    totalSupply := totalSupply + amount;
    balances[to] := balances[to] + amount;
  }

  method balanceOf(account: address) returns (balance: uint256)
  {
    return balances[account];
  }
}
