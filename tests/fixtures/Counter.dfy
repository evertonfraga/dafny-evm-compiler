class Counter {
  var count: uint256
  var maxValue: uint256

  invariant count <= maxValue

  method constructor()
    ensures count == 0
    ensures maxValue == 1000
  {
    count := 0;
    maxValue := 1000;
  }

  method increment() returns (newCount: uint256)
    requires count < maxValue
    ensures count == old(count) + 1
    ensures newCount == count
  {
    count := count + 1;
    return count;
  }

  method decrement() returns (newCount: uint256)
    requires count > 0
    ensures count == old(count) - 1
    ensures newCount == count
  {
    count := count - 1;
    return count;
  }

  method reset()
    ensures count == 0
  {
    count := 0;
  }

  method getCount() returns (value: uint256)
    ensures value == count
  {
    return count;
  }

  method setMaxValue(newMax: uint256)
    requires newMax >= count
    ensures maxValue == newMax
  {
    maxValue := newMax;
  }
}
