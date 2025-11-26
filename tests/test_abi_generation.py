import unittest
import json
from src.dafny_compiler import DafnyEVMCompiler
from src.compiler.abi_generator import ABIGenerator
from src.parser.dafny_parser import DafnyParser

class TestABIGeneration(unittest.TestCase):
    def setUp(self):
        self.compiler = DafnyEVMCompiler(verify=False)
        self.abi_gen = ABIGenerator()
    
    def test_simple_function_abi(self):
        """Test ABI generation for simple function"""
        source = """
        class Test {
          method getValue() returns (v: uint256) {
            return 42;
          }
        }
        """
        result = self.compiler.compile(source)
        self.assertTrue(result['success'])
        
        abi = json.loads(result['abi'])
        functions = [e for e in abi if e['type'] == 'function']
        self.assertEqual(len(functions), 1)
        self.assertEqual(functions[0]['name'], 'getValue')
        self.assertEqual(len(functions[0]['outputs']), 1)
        self.assertEqual(functions[0]['outputs'][0]['type'], 'uint256')
    
    def test_function_with_parameters(self):
        """Test ABI generation for function with parameters"""
        source = """
        class Test {
          method add(a: uint256, b: uint256) returns (result: uint256) {
            return a + b;
          }
        }
        """
        result = self.compiler.compile(source)
        self.assertTrue(result['success'])
        
        abi = json.loads(result['abi'])
        functions = [e for e in abi if e['type'] == 'function' and e['name'] == 'add']
        self.assertEqual(len(functions), 1)
        self.assertEqual(len(functions[0]['inputs']), 2)
        self.assertEqual(functions[0]['inputs'][0]['name'], 'a')
        self.assertEqual(functions[0]['inputs'][0]['type'], 'uint256')
        self.assertEqual(functions[0]['inputs'][1]['name'], 'b')
        self.assertEqual(functions[0]['inputs'][1]['type'], 'uint256')
    
    def test_multiple_return_values(self):
        """Test ABI generation for multiple return values"""
        source = """
        class Test {
          method getValues() returns (x: uint256, y: bool) {
            return 1, true;
          }
        }
        """
        result = self.compiler.compile(source)
        self.assertTrue(result['success'])
        
        abi = json.loads(result['abi'])
        functions = [e for e in abi if e['type'] == 'function']
        self.assertEqual(len(functions), 1)
        self.assertEqual(len(functions[0]['outputs']), 2)
        self.assertEqual(functions[0]['outputs'][0]['type'], 'uint256')
        self.assertEqual(functions[0]['outputs'][1]['type'], 'bool')
    
    def test_event_abi(self):
        """Test ABI generation for events"""
        source = """
        class Test {
          event Transfer(from: address, to: address, amount: uint256)
        }
        """
        result = self.compiler.compile(source)
        self.assertTrue(result['success'])
        
        abi = json.loads(result['abi'])
        events = [e for e in abi if e['type'] == 'event']
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['name'], 'Transfer')
        self.assertEqual(len(events[0]['inputs']), 3)
        self.assertEqual(events[0]['inputs'][0]['name'], 'from')
        self.assertEqual(events[0]['inputs'][0]['type'], 'address')
    
    def test_payable_function(self):
        """Test ABI generation for payable function"""
        source = """
        class Test {
          payable method deposit() {
            var x: uint256 := msg.value;
          }
        }
        """
        result = self.compiler.compile(source)
        self.assertTrue(result['success'])
        
        abi = json.loads(result['abi'])
        functions = [e for e in abi if e['type'] == 'function']
        self.assertEqual(len(functions), 1)
        self.assertEqual(functions[0]['stateMutability'], 'payable')
    
    def test_view_function(self):
        """Test ABI generation for view function"""
        source = """
        class Test {
          var value: uint256
          
          method getValue() view returns (v: uint256) {
            return value;
          }
        }
        """
        result = self.compiler.compile(source)
        self.assertTrue(result['success'])
        
        abi = json.loads(result['abi'])
        functions = [e for e in abi if e['type'] == 'function']
        self.assertEqual(len(functions), 1)
        self.assertEqual(functions[0]['stateMutability'], 'view')
    
    def test_pure_function(self):
        """Test ABI generation for pure function"""
        source = """
        class Test {
          method calculate(a: uint256, b: uint256) pure returns (result: uint256) {
            return a + b;
          }
        }
        """
        result = self.compiler.compile(source)
        self.assertTrue(result['success'])
        
        abi = json.loads(result['abi'])
        functions = [e for e in abi if e['type'] == 'function']
        self.assertEqual(len(functions), 1)
        self.assertEqual(functions[0]['stateMutability'], 'pure')
    
    def test_constructor_in_abi(self):
        """Test that constructor is included in ABI"""
        source = """
        class Test {
          var value: uint256
        }
        """
        result = self.compiler.compile(source)
        self.assertTrue(result['success'])
        
        abi = json.loads(result['abi'])
        constructors = [e for e in abi if e['type'] == 'constructor']
        self.assertEqual(len(constructors), 1)
        self.assertEqual(constructors[0]['stateMutability'], 'nonpayable')
    
    def test_complete_token_abi(self):
        """Test ABI generation for complete token contract"""
        source = """
        class Token {
          var balances: mapping<address, uint256>
          
          event Transfer(from: address, to: address, amount: uint256)
          
          method transfer(to: address, amount: uint256) returns (success: bool) {
            balances[msg.sender] := balances[msg.sender] - amount;
            balances[to] := balances[to] + amount;
            emit Transfer(msg.sender, to, amount);
            return true;
          }
          
          method balanceOf(account: address) view returns (balance: uint256) {
            return balances[account];
          }
        }
        """
        result = self.compiler.compile(source)
        self.assertTrue(result['success'])
        
        abi = json.loads(result['abi'])
        
        # Check we have constructor, 2 functions, and 1 event
        self.assertEqual(len([e for e in abi if e['type'] == 'constructor']), 1)
        self.assertEqual(len([e for e in abi if e['type'] == 'function']), 2)
        self.assertEqual(len([e for e in abi if e['type'] == 'event']), 1)
        
        # Check transfer function
        transfer = [e for e in abi if e.get('name') == 'transfer'][0]
        self.assertEqual(len(transfer['inputs']), 2)
        self.assertEqual(len(transfer['outputs']), 1)
        self.assertEqual(transfer['outputs'][0]['type'], 'bool')
        
        # Check balanceOf function
        balanceOf = [e for e in abi if e.get('name') == 'balanceOf'][0]
        self.assertEqual(balanceOf['stateMutability'], 'view')
        self.assertEqual(len(balanceOf['outputs']), 1)
        self.assertEqual(balanceOf['outputs'][0]['type'], 'uint256')

if __name__ == '__main__':
    unittest.main()
