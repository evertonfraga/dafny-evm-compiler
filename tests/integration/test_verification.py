import unittest
from src.dafny_compiler import DafnyEVMCompiler
from src.verifier.dafny_verifier import DafnyVerifier

class TestFormalVerification(unittest.TestCase):
    def setUp(self):
        try:
            self.verifier = DafnyVerifier()
            self.verification_available = True
        except FileNotFoundError:
            self.verification_available = False
            self.skipTest("Dafny verifier not installed")
    
    def test_verifier_finds_dafny(self):
        """Test that verifier can find Dafny executable"""
        self.assertIsNotNone(self.verifier.dafny_path)
    
    def test_valid_contract_verifies(self):
        """Test that a correct contract passes verification"""
        source = """
newtype Uint256 = x: int | 0 <= x <= 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff

class SimpleContract {
  var value: Uint256

  constructor()
    ensures value == 0
  {
    value := 0;
  }

  method setValue(v: Uint256)
    modifies this
    ensures value == v
  {
    value := v;
  }
}
"""
        result = self.verifier.verify(source)
        self.assertTrue(result['success'])
        self.assertTrue(result['verified'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_invalid_contract_fails_verification(self):
        """Test that an incorrect contract fails verification"""
        source = """
newtype Uint256 = x: int | 0 <= x <= 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff

class BrokenContract {
  var value: Uint256

  method broken(v: Uint256)
    modifies this
    ensures value == v + 1  // Wrong postcondition!
  {
    value := v;  // This doesn't satisfy the postcondition
  }
}
"""
        result = self.verifier.verify(source)
        self.assertTrue(result['success'])  # Verification ran
        self.assertFalse(result['verified'])  # But failed
        self.assertGreater(len(result['errors']), 0)
    
    def test_compiler_integration(self):
        """Test that compiler integrates verification"""
        source = """
newtype Uint256 = x: int | 0 <= x <= 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff

class VerifiedContract {
  var balance: Uint256

  constructor()
    ensures balance == 100
  {
    balance := 100;
  }

  method getBalance() returns (b: Uint256)
    ensures b == balance
  {
    return balance;
  }
}
"""
        compiler = DafnyEVMCompiler(verify=True)
        result = compiler.compile(source)
        
        self.assertTrue(result['success'])
        self.assertTrue(result['verified'])
        self.assertIn('bytecode', result)
    
    def test_compiler_rejects_unverified(self):
        """Test that compiler rejects contracts that fail verification"""
        source = """
newtype Uint256 = x: int | 0 <= x <= 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff

class BadContract {
  var value: Uint256

  method bad()
    modifies this
    ensures value == 10
  {
    value := 5;  // Doesn't satisfy postcondition
  }
}
"""
        compiler = DafnyEVMCompiler(verify=True)
        result = compiler.compile(source)
        
        self.assertFalse(result['success'])
        self.assertFalse(result['verified'])
        self.assertIn('verification_errors', result)
    
    def test_skip_verification_flag(self):
        """Test that verification can be skipped"""
        source = """
newtype Uint256 = x: int | 0 <= x <= 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff

class BadContract {
  var value: Uint256

  method bad()
    modifies this
    ensures value == 10
  {
    value := 5;
  }
}
"""
        compiler = DafnyEVMCompiler(verify=True)
        result = compiler.compile(source, skip_verification=True)
        
        # Should compile even though it wouldn't verify
        self.assertTrue(result['success'])
        self.assertFalse(result['verified'])

if __name__ == '__main__':
    unittest.main()
