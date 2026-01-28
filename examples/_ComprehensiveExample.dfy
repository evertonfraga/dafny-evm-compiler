// Comprehensive example demonstrating all Phase 3 features:
// - Structs
// - Multiple return values
// - Dynamic arrays
// - Inter-contract calls
// - Modulo operator

struct User {
  balance: uint256
  lastUpdate: uint256
}

class DeFiProtocol {
  var users: mapping<address, User>
  var userList: array<address>
  var totalDeposits: uint256
  var feeCollector: address
  
  event Deposit(user: address, amount: uint256)
  event Withdrawal(user: address, amount: uint256)
  
  constructor()
  {
    totalDeposits := 0;
  }
  
  // Multiple return values
  method getUserInfo(addr: address) returns (balance: uint256, lastUpdate: uint256)
  {
    var user: User := users[addr];
    return user.balance, user.lastUpdate;
  }
  
  // Dynamic arrays
  method addUser(addr: address)
    modifies this
  {
    userList.push(addr);
  }
  
  method getUserCount() returns (count: uint256)
  {
    return userList.length;
  }
  
  // Struct field access and assignment
  payable method deposit()
    modifies this
  {
    var user: User := users[msg.sender];
    user.balance := user.balance + msg.value;
    user.lastUpdate := block.timestamp;
    users[msg.sender] := user;
    totalDeposits := totalDeposits + msg.value;
    emit Deposit(msg.sender, msg.value);
  }
  
  method withdraw(amount: uint256)
    requires amount > 0
    modifies this
  {
    var user: User := users[msg.sender];
    if (user.balance >= amount) {
      user.balance := user.balance - amount;
      user.lastUpdate := block.timestamp;
      users[msg.sender] := user;
      totalDeposits := totalDeposits - amount;
      emit Withdrawal(msg.sender, amount);
    }
  }
  
  // Modulo operator for fee calculation
  method calculateFee(amount: uint256) returns (fee: uint256, remainder: uint256)
  {
    var feePercent: uint256 := 3;
    fee := amount / 100 * feePercent;
    remainder := amount % 100;
    return fee, remainder;
  }
  
  // Inter-contract call
  method callExternal(target: address, data: bytes32) returns (success: bool)
  {
    return target.call(data);
  }
  
  // Combining multiple features
  method processUsers(start: uint256, end: uint256) returns (processed: uint256)
    modifies this
  {
    var count: uint256 := 0;
    for (var i: uint256 := start; i < end; i := i + 1) {
      if (i < userList.length) {
        var addr: address := userList[i];
        var user: User := users[addr];
        user.lastUpdate := block.timestamp;
        users[addr] := user;
        count := count + 1;
      }
    }
    return count;
  }
}
