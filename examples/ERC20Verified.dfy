class ERC20Verified {
  // State variables
  var totalSupply: uint256
  var owner: address
  var paused: bool
  var balances: mapping<address, uint256>
  var allowances: mapping<address, mapping<address, uint256>>

  // Invariants
  invariant totalSupply >= 0
  invariant owner != 0

  constructor(initialSupply: uint256)
    requires initialSupply > 0
    modifies this
    ensures totalSupply == initialSupply
    ensures owner != 0
    ensures paused == false
  {
    totalSupply := initialSupply;
    owner := msg.sender;
    paused := false;
    balances := balances[msg.sender := initialSupply];
  }

  // Transfer tokens
  method transfer(to: address, amount: uint256) returns (success: bool)
    requires amount > 0
    requires to != 0
    requires balances[msg.sender] >= amount
    requires paused == false
    modifies this
    ensures totalSupply == old(totalSupply)
    ensures success == true
  {
    balances := balances[msg.sender := balances[msg.sender] - amount][to := balances[to] + amount];
    return true;
  }

  // Approve spender
  method approve(spender: address, amount: uint256) returns (success: bool)
    requires spender != 0
    requires paused == false
    modifies this
    ensures success == true
  {
    allowances := allowances[msg.sender := allowances[msg.sender][spender := amount]];
    return true;
  }

  // Transfer from approved account
  method transferFrom(from: address, to: address, amount: uint256) returns (success: bool)
    requires amount > 0
    requires to != 0
    requires balances[from] >= amount
    requires allowances[from][msg.sender] >= amount
    requires paused == false
    modifies this
    ensures totalSupply == old(totalSupply)
    ensures success == true
  {
    balances := balances[from := balances[from] - amount][to := balances[to] + amount];
    allowances := allowances[from := allowances[from][msg.sender := allowances[from][msg.sender] - amount]];
    return true;
  }

  // Mint new tokens (owner only)
  method mint(to: address, amount: uint256) returns (success: bool)
    requires amount > 0
    requires msg.sender == owner
    requires paused == false
    modifies this
    ensures totalSupply == old(totalSupply) + amount
    ensures success == true
  {
    totalSupply := totalSupply + amount;
    balances := balances[to := balances[to] + amount];
    return true;
  }

  // Burn tokens (owner only)
  method burn(from: address, amount: uint256) returns (success: bool)
    requires amount > 0
    requires msg.sender == owner
    requires amount <= totalSupply
    requires amount <= balances[from]
    requires paused == false
    modifies this
    ensures totalSupply == old(totalSupply) - amount
    ensures success == true
  {
    totalSupply := totalSupply - amount;
    balances := balances[from := balances[from] - amount];
    return true;
  }

  // Pause contract (owner only)
  method pause()
    requires msg.sender == owner
    requires paused == false
    modifies this
    ensures paused == true
  {
    paused := true;
  }

  // Unpause contract (owner only)
  method unpause()
    requires msg.sender == owner
    requires paused == true
    modifies this
    ensures paused == false
  {
    paused := false;
  }

  // View functions
  method balanceOf(account: address) returns (balance: uint256)
  {
    return balances[account];
  }

  method allowance(tokenOwner: address, spender: address) returns (remaining: uint256)
  {
    return allowances[tokenOwner][spender];
  }

  method getTotalSupply() returns (supply: uint256)
  {
    return totalSupply;
  }

  method getOwner() returns (ownerAddr: address)
  {
    return owner;
  }

  method isPaused() returns (status: bool)
  {
    return paused;
  }
}
