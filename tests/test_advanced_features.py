import unittest
from src.dafny_compiler import DafnyEVMCompiler
from src.parser.dafny_parser import DafnyParser
from src.parser.dafny_ast import *

def get_test_compiler():
    return DafnyEVMCompiler(verify=False)

class TestArraysAndMappings(unittest.TestCase):
    def test_parse_array_field(self):
        source = """
        class Test {
          var items: array<uint256>
        }
        """
        parser = DafnyParser(source)
        contract = parser.parse()
        
        self.assertEqual(len(contract.fields), 1)
        self.assertEqual(contract.fields[0].type.base, Type.ARRAY)
        self.assertEqual(contract.fields[0].type.element_type.base, Type.UINT256)
    
    def test_parse_mapping_field(self):
        source = """
        class Test {
          var balances: mapping<address, uint256>
        }
        """
        parser = DafnyParser(source)
        contract = parser.parse()
        
        self.assertEqual(len(contract.fields), 1)
        self.assertEqual(contract.fields[0].type.base, Type.MAPPING)
        self.assertEqual(contract.fields[0].type.key_type.base, Type.ADDRESS)
        self.assertEqual(contract.fields[0].type.value_type.base, Type.UINT256)
    
    def test_array_access(self):
        source = """
        class Test {
          var items: array<uint256>
          
          method getItem(index: uint256) returns (value: uint256) {
            return items[index];
          }
        }
        """
        parser = DafnyParser(source)
        contract = parser.parse()
        
        self.assertEqual(len(contract.methods), 1)
        ret_stmt = contract.methods[0].body[0]
        self.assertIsInstance(ret_stmt, Return)
        self.assertIsInstance(ret_stmt.value, ArrayAccess)
    
    def test_mapping_assignment(self):
        source = """
        class Test {
          var balances: mapping<address, uint256>
          
          method setBalance(addr: address, amount: uint256) {
            balances[addr] := amount;
          }
        }
        """
        parser = DafnyParser(source)
        contract = parser.parse()
        
        self.assertEqual(len(contract.methods), 1)
        assign_stmt = contract.methods[0].body[0]
        self.assertIsInstance(assign_stmt, Assignment)
        self.assertIsNotNone(assign_stmt.index)

class TestEvents(unittest.TestCase):
    def test_parse_event(self):
        source = """
        class Test {
          event Transfer(from: address, to: address, amount: uint256)
        }
        """
        parser = DafnyParser(source)
        contract = parser.parse()
        
        self.assertEqual(len(contract.events), 1)
        self.assertEqual(contract.events[0].name, "Transfer")
        self.assertEqual(len(contract.events[0].params), 3)
    
    def test_emit_event(self):
        source = """
        class Test {
          event Transfer(from: address, to: address, amount: uint256)
          
          method transfer(to: address, amount: uint256) {
            emit Transfer(to, to, amount);
          }
        }
        """
        parser = DafnyParser(source)
        contract = parser.parse()
        
        self.assertEqual(len(contract.methods), 1)
        emit_stmt = contract.methods[0].body[0]
        self.assertIsInstance(emit_stmt, EmitEvent)
        self.assertEqual(emit_stmt.name, "Transfer")
        self.assertEqual(len(emit_stmt.args), 3)

class TestPayable(unittest.TestCase):
    def test_parse_payable_method(self):
        source = """
        class Test {
          payable method deposit() returns (success: bool) {
            return true;
          }
        }
        """
        parser = DafnyParser(source)
        contract = parser.parse()
        
        self.assertEqual(len(contract.methods), 1)
        self.assertTrue(contract.methods[0].is_payable)
    
    def test_non_payable_method(self):
        source = """
        class Test {
          method withdraw() returns (success: bool) {
            return true;
          }
        }
        """
        parser = DafnyParser(source)
        contract = parser.parse()
        
        self.assertEqual(len(contract.methods), 1)
        self.assertFalse(contract.methods[0].is_payable)

class TestLibraryImports(unittest.TestCase):
    def test_parse_import(self):
        source = """
        import SafeMath from "SafeMath.sol"
        
        class Test {
          var value: uint256
        }
        """
        parser = DafnyParser(source)
        contract = parser.parse()
        
        self.assertEqual(len(contract.libraries), 1)
        self.assertEqual(contract.libraries[0].name, "SafeMath")
        self.assertEqual(contract.libraries[0].path, "SafeMath.sol")

class TestAdvancedCompilation(unittest.TestCase):
    def test_compile_with_mappings(self):
        source = """
        class Token {
          var balances: mapping<address, uint256>
          
          method setBalance(addr: address, amount: uint256) {
            balances[addr] := amount;
          }
          
          method getBalance(addr: address) returns (balance: uint256) {
            return balances[addr];
          }
        }
        """
        compiler = get_test_compiler()
        result = compiler.compile(source)
        
        self.assertTrue(result['success'], f"Compilation failed: {result.get('error')}")
        self.assertIn('keccak256', result['yul_code'])
    
    def test_compile_with_events(self):
        source = """
        class Token {
          var balance: uint256
          event Transfer(amount: uint256)
          
          method transfer(amount: uint256) {
            balance := amount;
            emit Transfer(amount);
          }
        }
        """
        compiler = get_test_compiler()
        result = compiler.compile(source)
        
        self.assertTrue(result['success'], f"Compilation failed: {result.get('error')}")
        self.assertIn('log', result['yul_code'])
    
    def test_compile_payable_method(self):
        source = """
        class Wallet {
          var balance: uint256
          
          payable method deposit() {
            balance := balance + 100;
          }
        }
        """
        compiler = get_test_compiler()
        result = compiler.compile(source)
        
        self.assertTrue(result['success'], f"Compilation failed: {result.get('error')}")
        # Payable methods should not have callvalue check
        yul = result['yul_code']
        self.assertIn('deposit', yul)

if __name__ == '__main__':
    unittest.main()
