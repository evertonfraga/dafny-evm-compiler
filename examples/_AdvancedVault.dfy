class AdvancedVault {
  var balance: uint256
  var owner: address
  var paused: bool
  
  // Events with indexed parameters
  event Deposit(address indexed user, uint256 amount, uint256 indexed timestamp)
  event Withdrawal(address indexed user, uint256 amount)
  event OwnershipTransferred(address indexed previousOwner, address indexed newOwner)
  event Paused(address indexed by)
  event Unpaused(address indexed by)
  
  // Custom errors
  error Unauthorized(address caller)
  error InsufficientBalance(uint256 requested, uint256 available)
  error ContractPaused()
  error ZeroAddress()
  
  // Receive function - accepts plain Ether transfers
  payable method receive() {
    balance := balance + msg.value;
    emit Deposit(msg.sender, msg.value, block.timestamp);
  }
  
  // Fallback function - called for unknown function calls
  method fallback() {
    revert("Unknown function");
  }
  
  // Deposit with explicit call
  payable method deposit() {
    if (paused) {
      revert ContractPaused();
    }
    balance := balance + msg.value;
    emit Deposit(msg.sender, msg.value, block.timestamp);
  }
  
  // Withdraw with custom error handling
  method withdraw(amount: uint256) {
    if (msg.sender != owner) {
      revert Unauthorized(msg.sender);
    }
    if (paused) {
      revert ContractPaused();
    }
    if (amount > balance) {
      revert InsufficientBalance(amount, balance);
    }
    balance := balance - amount;
    emit Withdrawal(msg.sender, amount);
  }
  
  // Transfer ownership
  method transferOwnership(newOwner: address) {
    if (msg.sender != owner) {
      revert Unauthorized(msg.sender);
    }
    if (newOwner == 0) {
      revert ZeroAddress();
    }
    var oldOwner: address := owner;
    owner := newOwner;
    emit OwnershipTransferred(oldOwner, newOwner);
  }
  
  // Pause contract
  method pause() {
    if (msg.sender != owner) {
      revert Unauthorized(msg.sender);
    }
    paused := true;
    emit Paused(msg.sender);
  }
  
  // Unpause contract
  method unpause() {
    if (msg.sender != owner) {
      revert Unauthorized(msg.sender);
    }
    paused := false;
    emit Unpaused(msg.sender);
  }
  
  // Get balance (view function)
  method getBalance() view returns (bal: uint256) {
    return balance;
  }
  
  // Emergency destroy
  method destroy() {
    if (msg.sender != owner) {
      revert Unauthorized(msg.sender);
    }
    selfdestruct(owner);
  }
}
