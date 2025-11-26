struct Person {
  age: uint256
  balance: uint256
}

class Registry {
  var owner: Person
  var count: uint256
  
  constructor()
    ensures count == 0
  {
    count := 0;
  }
  
  method setAge(newAge: uint256)
    modifies this
  {
    owner.age := newAge;
  }
  
  method getAge() returns (age: uint256)
  {
    return owner.age;
  }
  
  method increment()
    modifies this
  {
    count := count + 1;
  }
}
