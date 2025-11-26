import unittest
from src.dafny_compiler import DafnyEVMCompiler
from src.parser.dafny_parser import DafnyParser
from src.parser.dafny_ast import *

def get_test_compiler():
    return DafnyEVMCompiler(verify=False)

class TestStructs(unittest.TestCase):
    def test_parse_struct(self):
        source = """
        struct Person {
          age: uint256
          balance: uint256
        }
        
        class Test {
          var owner: Person
        }
        """
        parser = DafnyParser(source)
        contract = parser.parse()
        
        self.assertEqual(len(contract.structs), 1)
        self.assertEqual(contract.structs[0].name, "Person")
        self.assertEqual(len(contract.structs[0].fields), 2)
    
    def test_struct_compilation(self):
        source = """
        struct Person {
          age: uint256
          balance: uint256
        }
        
        class Test {
          var owner: Person
          
          method setAge(newAge: uint256) {
            owner.age := newAge;
          }
        }
        """
        compiler = get_test_compiler()
        result = compiler.compile(source)
        
        self.assertTrue(result['success'], f"Failed: {result.get('error')}")
        self.assertIn('sstore', result['yul_code'])

class TestMultipleReturns(unittest.TestCase):
    def test_parse_multiple_returns(self):
        source = """
        class Test {
          method getValues() returns (a: uint256, b: uint256) {
            return 1, 2;
          }
        }
        """
        parser = DafnyParser(source)
        contract = parser.parse()
        
        self.assertEqual(len(contract.methods), 1)
        self.assertIsInstance(contract.methods[0].returns, list)
        self.assertEqual(len(contract.methods[0].returns), 2)
    
    def test_multiple_return_compilation(self):
        source = """
        class Test {
          var x: uint256
          var y: uint256
          
          method getValues() returns (a: uint256, b: uint256) {
            return x, y;
          }
        }
        """
        compiler = get_test_compiler()
        result = compiler.compile(source)
        
        self.assertTrue(result['success'], f"Failed: {result.get('error')}")
        # Should store multiple values in memory
        self.assertIn('mstore(0,', result['yul_code'])
        self.assertIn('mstore(32,', result['yul_code'])

class TestDynamicArrays(unittest.TestCase):
    def test_array_length(self):
        source = """
        class Test {
          var items: array<uint256>
          
          method size() returns (len: uint256) {
            return items.length;
          }
        }
        """
        parser = DafnyParser(source)
        contract = parser.parse()
        
        ret_stmt = contract.methods[0].body[0]
        self.assertIsInstance(ret_stmt.value, ArrayLength)
    
    def test_array_push(self):
        source = """
        class Test {
          var items: array<uint256>
          
          method add(value: uint256) {
            items.push(value);
          }
        }
        """
        parser = DafnyParser(source)
        contract = parser.parse()
        
        push_stmt = contract.methods[0].body[0]
        self.assertIsInstance(push_stmt, ArrayPush)
    
    def test_array_pop(self):
        source = """
        class Test {
          var items: array<uint256>
          
          method remove() {
            items.pop();
          }
        }
        """
        parser = DafnyParser(source)
        contract = parser.parse()
        
        pop_stmt = contract.methods[0].body[0]
        self.assertIsInstance(pop_stmt, ArrayPop)
    
    def test_dynamic_array_compilation(self):
        source = """
        class Test {
          var items: array<uint256>
          
          method push(value: uint256) {
            items.push(value);
          }
          
          method size() returns (len: uint256) {
            return items.length;
          }
        }
        """
        compiler = get_test_compiler()
        result = compiler.compile(source)
        
        self.assertTrue(result['success'], f"Failed: {result.get('error')}")
        self.assertIn('keccak256_single', result['yul_code'])

class TestContractCalls(unittest.TestCase):
    def test_parse_call(self):
        source = """
        class Test {
          method callOther(addr: address, data: bytes32) returns (success: bool) {
            return addr.call(data);
          }
        }
        """
        parser = DafnyParser(source)
        contract = parser.parse()
        
        ret_stmt = contract.methods[0].body[0]
        self.assertIsInstance(ret_stmt.value, ContractCall)
        self.assertEqual(ret_stmt.value.method, 'call')
    
    def test_contract_call_compilation(self):
        source = """
        class Test {
          method callOther(addr: address) returns (success: bool) {
            var data: uint256 := 0;
            return addr.call(data);
          }
        }
        """
        compiler = get_test_compiler()
        result = compiler.compile(source)
        
        self.assertTrue(result['success'], f"Failed: {result.get('error')}")
        self.assertIn('call(gas()', result['yul_code'])

class TestModuloOperator(unittest.TestCase):
    def test_modulo(self):
        source = """
        class Test {
          method mod(a: uint256, b: uint256) returns (result: uint256) {
            return a % b;
          }
        }
        """
        compiler = get_test_compiler()
        result = compiler.compile(source)
        
        self.assertTrue(result['success'], f"Failed: {result.get('error')}")
        self.assertIn('mod(', result['yul_code'])

if __name__ == '__main__':
    unittest.main()
