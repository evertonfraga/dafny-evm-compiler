class ModernWallet {
  var owner: address
  var balance: uint256
  var lastUpdate: uint256
  var transactionCount: uint256
  var allowances: mapping<address, uint256>
  
  event Deposit(sender: address, amount: uint256, timestamp: uint256)
  event Withdrawal(recipient: address, amount: uint256)
  event AllowanceSet(spender: address, amount: uint256)
  
  invariant balance >= 0
  invariant transactionCount >= 0
  
  constructor()
    ensures owner == msg.sender
    ensures balance == 0
  {
    owner := msg.sender;
    balance := 0;
    transactionCount := 0;
    lastUpdate := block.timestamp;
  }
  
  payable method deposit() returns (success: bool)
    requires msg.value > 0
    ensures balance == old(balance) + msg.value
  {
    balance := balance + msg.value;
    lastUpdate := block.timestamp;
    transactionCount := transactionCount + 1;
    emit Deposit(msg.sender, msg.value, block.timestamp);
    return true;
  }
  
  method withdraw(amount: uint256) returns (success: bool)
    requires amount > 0
    requires amount <= balance
  {
    if (msg.sender == owner) {
      if (amount <= balance) {
        balance := balance - amount;
        lastUpdate := block.timestamp;
        transactionCount := transactionCount + 1;
        emit Withdrawal(msg.sender, amount);
        return true;
      }
    }
    return false;
  }
  
  method setAllowance(spender: address, amount: uint256)
    requires msg.sender == owner
  {
    allowances[spender] := amount;
    emit AllowanceSet(spender, amount);
  }
  
  method withdrawWithAllowance(amount: uint256) returns (success: bool)
    requires amount > 0
  {
    var allowed: uint256 := allowances[msg.sender];
    if (allowed >= amount) {
      if (balance >= amount) {
        balance := balance - amount;
        allowances[msg.sender] := allowed - amount;
        emit Withdrawal(msg.sender, amount);
        return true;
      }
    }
    return false;
  }
  
  method getBalance() returns (bal: uint256)
    ensures bal == balance
  {
    return balance;
  }
  
  method getOwner() returns (addr: address)
    ensures addr == owner
  {
    return owner;
  }
  
  method getLastUpdate() returns (timestamp: uint256)
  {
    return lastUpdate;
  }
  
  method isOwner() returns (result: bool)
  {
    if (msg.sender == owner) {
      return true;
    }
    return false;
  }
  
  method batchProcess(count: uint8)
  {
    var i: uint8 := 0;
    while (i < count) {
      transactionCount := transactionCount + 1;
      i := i + 1;
    }
  }
  
  method processRange(start: uint256, end: uint256)
  {
    for (var i: uint256 := start; i < end; i := i + 1) {
      transactionCount := transactionCount + 1;
    }
  }
}
