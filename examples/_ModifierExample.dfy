// Example demonstrating custom modifiers for access control

class AccessControlled {
  var owner: address
  var paused: bool
  var balance: uint256
  
  event OwnershipTransferred(previousOwner: address, newOwner: address)
  event Paused()
  event Unpaused()
  
  constructor()
  {
    owner := msg.sender;
    paused := false;
    balance := 0;
  }
  
  // Custom modifiers
  modifier onlyOwner() {
    require(msg.sender == owner);
  }
  
  modifier whenNotPaused() {
    require(!paused);
  }
  
  modifier whenPaused() {
    require(paused);
  }
  
  // Methods using modifiers
  method transferOwnership(newOwner: address) onlyOwner
    modifies this
  {
    var oldOwner: address := owner;
    owner := newOwner;
    emit OwnershipTransferred(oldOwner, newOwner);
  }
  
  method pause() onlyOwner whenNotPaused
    modifies this
  {
    paused := true;
    emit Paused();
  }
  
  method unpause() onlyOwner whenPaused
    modifies this
  {
    paused := false;
    emit Unpaused();
  }
  
  payable method deposit() whenNotPaused
    modifies this
  {
    balance := balance + msg.value;
  }
  
  method withdraw(amount: uint256) onlyOwner whenNotPaused
    requires amount <= balance
    modifies this
  {
    balance := balance - amount;
  }
  
  method getBalance() view returns (b: uint256)
  {
    return balance;
  }
}
