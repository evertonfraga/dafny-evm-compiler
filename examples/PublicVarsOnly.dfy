class PublicVarsOnly {
  public var totalSupply: uint256
  public var balances: mapping<address, uint256>

  constructor()
    modifies this
    ensures totalSupply == 1000000
  {
    totalSupply := 1000000;
  }
}
