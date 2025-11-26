import SafeMath from "SafeMath.sol"

class AdvancedToken {
  var balances: mapping<address, uint256>
  var allowances: mapping<address, uint256>
  var holders: array<address>
  var totalSupply: uint256
  var owner: address

  event Transfer(from: address, to: address, amount: uint256)
  event Approval(owner: address, spender: address, amount: uint256)
  event Deposit(sender: address, amount: uint256)

  invariant totalSupply >= 0

  method constructor(initialSupply: uint256)
    requires initialSupply > 0
    ensures totalSupply == initialSupply
  {
    totalSupply := initialSupply;
    balances[owner] := initialSupply;
    emit Transfer(owner, owner, initialSupply);
  }

  method transfer(to: address, amount: uint256) returns (success: bool)
    requires amount > 0
    requires balances[owner] >= amount
    ensures balances[owner] == old(balances[owner]) - amount
  {
    var senderBalance: uint256 := balances[owner];
    balances[owner] := senderBalance - amount;
    balances[to] := balances[to] + amount;
    emit Transfer(owner, to, amount);
    return true;
  }

  method approve(spender: address, amount: uint256) returns (success: bool)
    requires amount > 0
  {
    allowances[spender] := amount;
    emit Approval(owner, spender, amount);
    return true;
  }

  method balanceOf(account: address) returns (balance: uint256)
  {
    return balances[account];
  }

  payable method deposit() returns (success: bool)
  {
    balances[owner] := balances[owner] + 1000;
    totalSupply := totalSupply + 1000;
    emit Deposit(owner, 1000);
    return true;
  }

  method getHolder(index: uint256) returns (holder: address)
    requires index < 100
  {
    return holders[index];
  }
}
