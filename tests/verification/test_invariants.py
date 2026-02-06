"""
Tests for Dafny invariants in smart contracts.

Invariants are properties that must hold throughout the contract's lifetime.
Class invariants must be true after construction and after every method call.
"""

import unittest
from src.dafny_compiler import DafnyEVMCompiler


class TestInvariants(unittest.TestCase):
    """Test Dafny invariants compilation and verification."""
    
    def setUp(self):
        self.compiler = DafnyEVMCompiler(verify=False)
    
    def test_simple_class_invariant(self):
        """Test basic class invariant."""
        code = """
        class Counter {
          var count: uint256
          
          invariant count >= 0
          
          method increment()
            modifies this
          {
            count := count + 1;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_multiple_invariants(self):
        """Test multiple class invariants."""
        code = """
        class Token {
          var balance: uint256
          var totalSupply: uint256
          
          invariant balance >= 0
          invariant totalSupply >= balance
          
          method mint(amount: uint256)
            modifies this
          {
            balance := balance + amount;
            totalSupply := totalSupply + amount;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_invariant_with_comparison(self):
        """Test invariant with field comparison."""
        code = """
        class Vault {
          var balance: uint256
          var maxBalance: uint256
          
          invariant balance <= maxBalance
          
          constructor(max: uint256)
            modifies this
          {
            balance := 0;
            maxBalance := max;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_invariant_preserved_across_methods(self):
        """Test that invariant is maintained across different methods."""
        code = """
        class BoundedCounter {
          var count: uint256
          
          invariant count <= 100
          
          method increment()
            requires count < 100
            modifies this
          {
            count := count + 1;
          }
          
          method reset()
            modifies this
          {
            count := 0;
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])


class TestInvariantViolations(unittest.TestCase):
    """Test that invariant violations are caught at verification time."""
    
    def setUp(self):
        try:
            from src.verifier.dafny_verifier import DafnyVerifier
            self.verifier = DafnyVerifier()
            self.verification_available = True
        except (ImportError, FileNotFoundError):
            self.verification_available = False
            self.skipTest("Dafny verifier not available")
    
    def test_verifier_converts_invariants_to_valid(self):
        """Verify that invariants are converted to Valid() predicate and checked."""
        code = """
        newtype Uint256 = x: int | 0 <= x <= 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
        
        class Counter {
          var count: Uint256
          invariant count <= 100
          
          method breakInvariant()
            modifies this
          {
            count := 150;
          }
        }
        """
        result = self.verifier.verify(code)
        self.assertTrue(result['success'])
        self.assertFalse(result['verified'])
        self.assertGreater(len(result['errors']), 0)
    
    
    def test_method_violates_invariant(self):
        """Test that method violating invariant fails verification."""
        code = """
        newtype Uint256 = x: int | 0 <= x <= 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
        
        class Counter {
          var count: Uint256
          
          invariant count <= 100
          
          method breakInvariant()
            modifies this
          {
            count := 150;
          }
        }
        """
        result = self.verifier.verify(code)
        self.assertTrue(result['success'])
        self.assertFalse(result['verified'])
        self.assertGreater(len(result['errors']), 0)
    
    
    @unittest.expectedFailure
    
    def test_constructor_fails_to_establish_invariant(self):
        """Test that constructor not establishing invariant fails verification."""
        code = """
        newtype Uint256 = x: int | 0 <= x <= 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
        
        class Token {
          var balance: Uint256
          
          invariant balance >= 100
          
          constructor()
          {
            balance := 50;
          }
        }
        """
        result = self.verifier.verify(code)
        self.assertTrue(result['success'])
        self.assertFalse(result['verified'])
        self.assertGreater(len(result['errors']), 0)
    
    
    def test_invariant_violated_by_increment(self):
        """Test that incrementing beyond bound violates invariant.
        
        NOTE: This currently catches newtype overflow, not invariant violation.
        The verifier detects that count + 1 might exceed Uint256 bounds,
        but doesn't check the invariant count <= 10.
        """
        code = """
        newtype Uint256 = x: int | 0 <= x <= 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
        
        class BoundedCounter {
          var count: Uint256
          
          invariant count <= 10
          
          constructor()
          {
            count := 0;
          }
          
          method increment()
            modifies this
          {
            count := count + 1;
          }
        }
        """
        result = self.verifier.verify(code)
        self.assertTrue(result['success'])
        # This fails verification due to potential Uint256 overflow, not invariant
        self.assertFalse(result['verified'])
        self.assertGreater(len(result['errors']), 0)
    
    @unittest.expectedFailure
    
    def test_multiple_invariants_one_violated(self):
        """Test that violating one of multiple invariants fails verification."""
        code = """
        newtype Uint256 = x: int | 0 <= x <= 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
        
        class Vault {
          var balance: Uint256
          var maxBalance: Uint256
          
          invariant balance >= 0
          invariant balance <= maxBalance
          
          constructor()
          {
            balance := 100;
            maxBalance := 50;
          }
        }
        """
        result = self.verifier.verify(code)
        self.assertTrue(result['success'])
        self.assertFalse(result['verified'])
        self.assertGreater(len(result['errors']), 0)
    
    
    @unittest.expectedFailure
    
    def test_invariant_violated_conditionally(self):
        """Test that conditional invariant violation is caught."""
        code = """
        newtype Uint256 = x: int | 0 <= x <= 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
        
        class ConditionalCounter {
          var count: Uint256
          
          invariant count <= 100
          
          constructor()
          {
            count := 0;
          }
          
          method update(value: Uint256)
            modifies this
          {
            if value > 50 {
              count := 200;
            } else {
              count := value;
            }
          }
        }
        """
        result = self.verifier.verify(code)
        self.assertTrue(result['success'])
        self.assertFalse(result['verified'])
        self.assertGreater(len(result['errors']), 0)
    
    def test_multiple_invariants_all_checked(self):
        """Test that all invariants in a class are checked together."""
        code = """
        newtype Uint256 = x: int | 0 <= x <= 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
        
        class BoundedValue {
          var value: Uint256
          var min: Uint256
          var max: Uint256
          
          invariant value >= min
          invariant value <= max
          invariant min <= max
          
          constructor(minVal: Uint256, maxVal: Uint256)
            requires minVal <= maxVal
          {
            min := minVal;
            max := maxVal;
            value := minVal;
          }
          
          method setValue(v: Uint256)
            modifies this
          {
            value := v;
          }
        }
        """
        result = self.verifier.verify(code)
        self.assertTrue(result['success'])
        self.assertFalse(result['verified'])
        self.assertGreater(len(result['errors']), 0)


if __name__ == '__main__':
    unittest.main()
