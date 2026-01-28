class DafnyToken {
  // Metadata
  var name: string
  var symbol: string
  var totalSupply: uint256
  var owner: address
  var balances: mapping<address, uint256>
  var allowances: mapping<address, mapping<address, uint256>>

  // Events
  event Transfer(from: address, to: address, amount: uint256)
  event Approval(owner: address, spender: address, amount: uint256)
  event Mint(to: address, amount: uint256)
  event Burn(from: address, amount: uint256)

  // Invariants
  invariant totalSupply >= 0
  invariant owner != 0

  constructor(initialSupply: uint256)
    requires initialSupply > 0
    modifies this
    ensures totalSupply == initialSupply
    ensures owner == msg.sender
    ensures balances[msg.sender] == initialSupply
  {
    name := "Dafny Token";
    symbol := "DFY";
    totalSupply := initialSupply;
    owner := msg.sender;
    balances := balances[msg.sender := initialSupply];
    emit Transfer(0, msg.sender, initialSupply);
  }

  // Mint tokens - anyone can mint
  method mint(amount: uint256)
    requires amount > 0
    modifies this
    ensures totalSupply == old(totalSupply) + amount
    ensures balances[msg.sender] == old(balances[msg.sender]) + amount
  {
    totalSupply := totalSupply + amount;
    balances[msg.sender] := balances[msg.sender] + amount;
    emit Mint(msg.sender, amount);
    emit Transfer(0, msg.sender, amount);
  }

  // Burn own tokens
  method burn(amount: uint256)
    requires amount > 0
    requires balances[msg.sender] >= amount
    modifies this
    ensures totalSupply == old(totalSupply) - amount
    ensures balances[msg.sender] == old(balances[msg.sender]) - amount
  {
    balances[msg.sender] := balances[msg.sender] - amount;
    totalSupply := totalSupply - amount;
    emit Burn(msg.sender, amount);
    emit Transfer(msg.sender, 0, amount);
  }

  // Transfer tokens
  method transfer(to: address, amount: uint256) returns (success: bool)
    requires amount > 0
    requires to != 0
    requires balances[msg.sender] >= amount
    modifies this
    ensures balances[msg.sender] == old(balances[msg.sender]) - amount
    ensures balances[to] == old(balances[to]) + amount
  {
    balances[msg.sender] := balances[msg.sender] - amount;
    balances[to] := balances[to] + amount;
    emit Transfer(msg.sender, to, amount);
    return true;
  }

  // Approve spending
  method approve(spender: address, amount: uint256) returns (success: bool)
    requires spender != 0
    modifies this
    ensures allowances[msg.sender][spender] == amount
  {
    allowances[msg.sender][spender] := amount;
    emit Approval(msg.sender, spender, amount);
    return true;
  }

  // Transfer from approved address
  method transferFrom(from: address, to: address, amount: uint256) returns (success: bool)
    requires amount > 0
    requires from != 0
    requires to != 0
    requires balances[from] >= amount
    requires allowances[from][msg.sender] >= amount
    modifies this
    ensures balances[from] == old(balances[from]) - amount
    ensures balances[to] == old(balances[to]) + amount
    ensures allowances[from][msg.sender] == old(allowances[from][msg.sender]) - amount
  {
    balances[from] := balances[from] - amount;
    balances[to] := balances[to] + amount;
    allowances[from][msg.sender] := allowances[from][msg.sender] - amount;
    emit Transfer(from, to, amount);
    return true;
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
}
