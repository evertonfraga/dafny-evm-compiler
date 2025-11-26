import unittest
from src.dafny_compiler import DafnyEVMCompiler
from src.parser.dafny_parser import DafnyParser
from src.parser.dafny_ast import *

# Use compiler without verification for syntax tests
def get_test_compiler():
    return DafnyEVMCompiler(verify=False)

class TestGlobalVariables(unittest.TestCase):
    def test_msg_sender(self):
        source = """
        class Test {
          var owner: address
          
          method setOwner() {
            owner := msg.sender;
          }
        }
        """
        compiler = get_test_compiler()
        result = compiler.compile(source)
        
        self.assertTrue(result['success'], f"Failed: {result.get('error')}")
        self.assertIn('caller()', result['yul_code'])
    
    def test_msg_value(self):
        source = """
        class Test {
          var balance: uint256
          
          payable method deposit() {
            balance := msg.value;
          }
        }
        """
        compiler = get_test_compiler()
        result = compiler.compile(source)
        
        self.assertTrue(result['success'], f"Failed: {result.get('error')}")
        self.assertIn('callvalue()', result['yul_code'])
    
    def test_block_timestamp(self):
        source = """
        class Test {
          var lastUpdate: uint256
          
          method update() {
            lastUpdate := block.timestamp;
          }
        }
        """
        compiler = get_test_compiler()
        result = compiler.compile(source)
        
        self.assertTrue(result['success'], f"Failed: {result.get('error')}")
        self.assertIn('timestamp()', result['yul_code'])
    
    def test_block_number(self):
        source = """
        class Test {
          var blockNum: uint256
          
          method saveBlock() {
            blockNum := block.number;
          }
        }
        """
        compiler = get_test_compiler()
        result = compiler.compile(source)
        
        self.assertTrue(result['success'], f"Failed: {result.get('error')}")
        self.assertIn('number()', result['yul_code'])

class TestControlFlow(unittest.TestCase):
    def test_if_statement(self):
        source = """
        class Test {
          var value: uint256
          
          method conditional(x: uint256) {
            if (x > 10) {
              value := 100;
            }
          }
        }
        """
        compiler = get_test_compiler()
        result = compiler.compile(source)
        
        self.assertTrue(result['success'], f"Failed: {result.get('error')}")
        self.assertIn('if gt(x, 10)', result['yul_code'])
    
    def test_if_else_statement(self):
        source = """
        class Test {
          var value: uint256
          
          method conditional(x: uint256) {
            if (x > 10) {
              value := 100;
            } else {
              value := 50;
            }
          }
        }
        """
        compiler = get_test_compiler()
        result = compiler.compile(source)
        
        self.assertTrue(result['success'], f"Failed: {result.get('error')}")
        yul = result['yul_code']
        self.assertIn('if gt(x, 10)', yul)
        self.assertIn('iszero(gt(x, 10))', yul)
    
    def test_while_loop(self):
        source = """
        class Test {
          var counter: uint256
          
          method loop() {
            while (counter < 10) {
              counter := counter + 1;
            }
          }
        }
        """
        compiler = get_test_compiler()
        result = compiler.compile(source)
        
        self.assertTrue(result['success'], f"Failed: {result.get('error')}")
        self.assertIn('for { } lt(', result['yul_code'])
    
    def test_for_loop(self):
        source = """
        class Test {
          var sum: uint256
          
          method loop() {
            for (var i: uint256 := 0; i < 10; i := i + 1) {
              sum := sum + i;
            }
          }
        }
        """
        compiler = get_test_compiler()
        result = compiler.compile(source)
        
        self.assertTrue(result['success'], f"Failed: {result.get('error')}")
        self.assertIn('for {', result['yul_code'])

class TestExtendedTypes(unittest.TestCase):
    def test_uint8(self):
        source = """
        class Test {
          var small: uint8
          
          method set(x: uint8) {
            small := x;
          }
        }
        """
        parser = DafnyParser(source)
        contract = parser.parse()
        
        self.assertEqual(contract.fields[0].type.base, Type.UINT8)
    
    def test_uint128(self):
        source = """
        class Test {
          var medium: uint128
        }
        """
        parser = DafnyParser(source)
        contract = parser.parse()
        
        self.assertEqual(contract.fields[0].type.base, Type.UINT128)
    
    def test_bytes32(self):
        source = """
        class Test {
          var hash: bytes32
        }
        """
        parser = DafnyParser(source)
        contract = parser.parse()
        
        self.assertEqual(contract.fields[0].type.base, Type.BYTES32)

class TestBuiltinFunctions(unittest.TestCase):
    def test_keccak256(self):
        source = """
        class Test {
          var hash: bytes32
          
          method computeHash(data: bytes32) {
            hash := keccak256(data);
          }
        }
        """
        compiler = get_test_compiler()
        result = compiler.compile(source)
        
        self.assertTrue(result['success'], f"Failed: {result.get('error')}")
        self.assertIn('keccak256_hash', result['yul_code'])
    
    def test_gasleft(self):
        source = """
        class Test {
          var gasRemaining: uint256
          
          method checkGas() {
            gasRemaining := gasleft();
          }
        }
        """
        compiler = get_test_compiler()
        result = compiler.compile(source)
        
        self.assertTrue(result['success'], f"Failed: {result.get('error')}")
        self.assertIn('gas()', result['yul_code'])

class TestIntegration(unittest.TestCase):
    def test_complete_contract(self):
        source = """
        class Wallet {
          var owner: address
          var balance: uint256
          var lastUpdate: uint256
          
          event Deposit(sender: address, amount: uint256)
          
          method constructor() {
            owner := msg.sender;
            balance := 0;
          }
          
          payable method deposit() {
            if (msg.value > 0) {
              balance := balance + msg.value;
              lastUpdate := block.timestamp;
              emit Deposit(msg.sender, msg.value);
            }
          }
          
          method withdraw(amount: uint256) {
            if (msg.sender == owner) {
              if (amount <= balance) {
                balance := balance - amount;
              }
            }
          }
        }
        """
        compiler = get_test_compiler()
        result = compiler.compile(source)
        
        self.assertTrue(result['success'], f"Failed: {result.get('error')}")
        yul = result['yul_code']
        self.assertIn('caller()', yul)
        self.assertIn('callvalue()', yul)
        self.assertIn('timestamp()', yul)
        self.assertIn('if eq(', yul)  # Check for equality comparison

if __name__ == '__main__':
    unittest.main()
