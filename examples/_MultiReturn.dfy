class Math {
  var x: uint256
  var y: uint256
  
  constructor()
  {
    x := 10;
    y := 20;
  }
  
  method getValues() returns (a: uint256, b: uint256)
  {
    return x, y;
  }
  
  method divMod(dividend: uint256, divisor: uint256) returns (quotient: uint256, remainder: uint256)
    requires divisor > 0
  {
    return dividend / divisor, dividend % divisor;
  }
}
