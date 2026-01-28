class SimpleTest {
  var value: uint256

  constructor()
    modifies this
  {
    value := 42;
  }

  method getValue() returns (result: uint256)
  {
    return value;
  }
}
