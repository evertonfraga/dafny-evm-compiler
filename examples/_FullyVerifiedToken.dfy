class FullyVerifiedToken {
  var totalSupply: uint256
  var balances: mapping<address, uint256>

  constructor()
    modifies this
    ensures totalSupply == 1000000
  {
    totalSupply := 1000000;
    balances := map[];
  }

  method mint(to: address, amount: uint256)
    requires amount > 0
    requires totalSupply + amount <= 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
    modifies this
    ensures totalSupply == old(totalSupply) + amount
  {
    var currentBalance: uint256 := if to in balances then balances[to] else 0;
    totalSupply := totalSupply + amount;
    balances[to] := currentBalance + amount;
  }

  method balanceOf(account: address) returns (balance: uint256)
    ensures balance == (if account in balances then balances[account] else 0)
  {
    if account in balances {
      return balances[account];
    } else {
      return 0;
    }
  }

  method getTotalSupply() returns (supply: uint256)
    ensures supply == totalSupply
  {
    return totalSupply;
  }

  method transfer(sender: address, to: address, amount: uint256) returns (success: bool)
    requires amount > 0
    requires sender in balances
    requires balances[sender] >= amount
    modifies this
  {
    var toBalance: uint256 := if to in balances then balances[to] else 0;
    balances[sender] := balances[sender] - amount;
    balances[to] := toBalance + amount;
    return true;
  }
}
