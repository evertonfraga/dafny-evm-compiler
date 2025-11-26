class Stack {
  var items: array<uint256>
  
  constructor()
  {
    // Array starts empty
  }
  
  method push(value: uint256)
    modifies this
  {
    items.push(value);
  }
  
  method pop()
    modifies this
  {
    items.pop();
  }
  
  method size() returns (len: uint256)
  {
    return items.length;
  }
  
  method get(index: uint256) returns (value: uint256)
  {
    return items[index];
  }
}
