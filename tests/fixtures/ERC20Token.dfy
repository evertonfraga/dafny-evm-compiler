class ERC20Token {
  var totalSupply: uint256
  var owner: address
  var paused: bool

  invariant totalSupply >= 0
  invariant paused == true || paused == false

  constructor(initialSupply: uint256)
    requires initialSupply > 0
    modifies this
    ensures totalSupply == initialSupply
    ensures paused == false
  {
    totalSupply := initialSupply;
    owner := 0;
    paused := false;
  }

  method mint(amount: uint256) returns (success: bool)
    requires amount > 0
    requires paused == false
    modifies this
    ensures totalSupply == old(totalSupply) + amount
  {
    totalSupply := totalSupply + amount;
    return true;
  }

  method burn(amount: uint256) returns (success: bool)
    requires amount > 0
    requires amount <= totalSupply
    requires paused == false
    modifies this
    ensures totalSupply == old(totalSupply) - amount
  {
    totalSupply := totalSupply - amount;
    return true;
  }

  method pause()
    requires paused == false
    modifies this
    ensures paused == true
  {
    paused := true;
  }

  method unpause()
    requires paused == true
    modifies this
    ensures paused == false
  {
    paused := false;
  }

  method getTotalSupply() returns (supply: uint256)
    ensures supply == totalSupply
  {
    return totalSupply;
  }

  method isPaused() returns (status: bool)
    ensures status == paused
  {
    return paused;
  }
}
