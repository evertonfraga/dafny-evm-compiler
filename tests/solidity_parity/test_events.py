"""
Tests for Solidity-compatible event declarations and emissions.

Events provide logging functionality for smart contracts.
They are compiled to EVM LOG opcodes and included in the ABI.
"""

import unittest
import json
from src.dafny_compiler import DafnyEVMCompiler
from src.parser.dafny_parser import DafnyParser
from src.translator.yul_generator import YulGenerator
from src.compiler.abi_generator import ABIGenerator


class TestEvents(unittest.TestCase):
    """Test event declaration, emission, and ABI generation."""
    
    def setUp(self):
        self.compiler = DafnyEVMCompiler(verify=False)
    
    def test_simple_event_declaration(self):
        """Test basic event with single parameter."""
        code = """
        class Token {
          event Transfer(to: address, amount: uint256)
          
          var balance: uint256
          
          method transfer(to: address, amount: uint256)
            modifies this
          {
            balance := balance - amount;
            emit Transfer(to, amount);
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_event_with_indexed_parameters(self):
        """Test event with indexed parameters for filtering."""
        code = """
        class Token {
          event Transfer(indexed from: address, indexed to: address, amount: uint256)
          
          method transfer(to: address, amount: uint256)
            modifies this
          {
            emit Transfer(msg.sender, to, 100);
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_event_emission(self):
        """Test emit statement generates LOG opcode."""
        code = """
        class Token {
          event Transfer(to: address, amount: uint256)
          
          method transfer(to: address, amount: uint256)
            modifies this
          {
            emit Transfer(to, amount);
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
        
        # Check Yul contains log
        yul = result.get('yul_code', '')
        self.assertIn("log", yul.lower())
    
    def test_multiple_events(self):
        """Test contract with multiple event types."""
        code = """
        class Token {
          event Transfer(from: address, to: address, amount: uint256)
          event Approval(owner: address, spender: address, amount: uint256)
          
          method transfer(to: address, amount: uint256)
            modifies this
          {
            emit Transfer(msg.sender, to, amount);
          }
          
          method approve(spender: address, amount: uint256)
            modifies this
          {
            emit Approval(msg.sender, spender, amount);
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
    
    def test_event_abi_generation(self):
        """Test event appears correctly in ABI."""
        code = """
        class Token {
          event Transfer(indexed from: address, indexed to: address, amount: uint256)
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])
        
        abi = json.loads(result.get('abi', '[]'))
        
        # Find event in ABI
        event_abi = None
        for item in abi:
            if item.get('type') == 'event' and item.get('name') == 'Transfer':
                event_abi = item
                break
        
        self.assertIsNotNone(event_abi)
        self.assertEqual(len(event_abi['inputs']), 3)
    
    def test_event_with_no_parameters(self):
        """Test event with no parameters."""
        code = """
        class Contract {
          event Triggered()
          
          method trigger()
            modifies this
          {
            emit Triggered();
          }
        }
        """
        result = self.compiler.compile(code, skip_verification=True)
        self.assertTrue(result['success'])


if __name__ == '__main__':
    unittest.main()



class TestEvents(unittest.TestCase):
    """Test event declaration, emission, and ABI generation."""
    
    def test_simple_event_declaration(self):
        """Test basic event with single parameter."""
        code = """
        class Token {
          event Transfer(to: address, amount: uint256)
          
          var balance: uint256
          
          method transfer(to: address, amount: uint256)
            modifies this
          {
            balance := balance - amount;
            emit Transfer(to, amount);
          }
        }
        """
        parser = DafnyParser(code)
        ast = parser.parse()
        
        self.assertEqual(len(ast.events), 1)
        event = ast.events[0]
        self.assertEqual(event.name, "Transfer")
        self.assertEqual(len(event.params), 2)
    
    def test_event_with_indexed_parameters(self):
        """Test event with indexed parameters for filtering."""
        code = """
        class Token {
          event Transfer(indexed from: address, indexed to: address, amount: uint256)
          
          method transfer(to: address, amount: uint256)
            modifies this
          {
            emit Transfer(msg.sender, to, 100);
          }
        }
        """
        parser = DafnyParser(code)
        ast = parser.parse()
        
        event = ast.events[0]
        self.assertEqual(len(event.params), 3)
        # First two should be indexed
        self.assertTrue(event.indexed[0])
        self.assertTrue(event.indexed[1])
        self.assertFalse(event.indexed[2])
    
    def test_event_emission(self):
        """Test emit statement generates LOG opcode."""
        code = """
        class Token {
          event Transfer(to: address, amount: uint256)
          
          method transfer(to: address, amount: uint256)
            modifies this
          {
            emit Transfer(to, amount);
          }
        }
        """
        parser = DafnyParser(code)
        ast = parser.parse()
        
        # Check emit statement in AST
        method = ast.methods[0]
        self.assertEqual(len(method.body), 1)
        
        # Generate Yul and check for log
        generator = YulGenerator()
        yul = generator.generate(ast)
        self.assertIn("log", yul.lower())
    
    def test_multiple_events(self):
        """Test contract with multiple event types."""
        code = """
        class Token {
          event Transfer(from: address, to: address, amount: uint256)
          event Approval(owner: address, spender: address, amount: uint256)
          
          method transfer(to: address, amount: uint256)
            modifies this
          {
            emit Transfer(msg.sender, to, amount);
          }
          
          method approve(spender: address, amount: uint256)
            modifies this
          {
            emit Approval(msg.sender, spender, amount);
          }
        }
        """
        parser = DafnyParser(code)
        ast = parser.parse()
        
        self.assertEqual(len(ast.events), 2)
        self.assertEqual(ast.events[0].name, "Transfer")
        self.assertEqual(ast.events[1].name, "Approval")
    
    def test_event_abi_generation(self):
        """Test event appears correctly in ABI."""
        code = """
        class Token {
          event Transfer(indexed from: address, indexed to: address, amount: uint256)
        }
        """
        parser = DafnyParser(code)
        ast = parser.parse()
        
        abi_gen = ABIGenerator()
        abi_json = abi_gen.generate(ast)
        abi = json.loads(abi_json)
        
        # Find event in ABI
        event_abi = None
        for item in abi:
            if item.get('type') == 'event' and item.get('name') == 'Transfer':
                event_abi = item
                break
        
        self.assertIsNotNone(event_abi)
        self.assertEqual(len(event_abi['inputs']), 3)
        # Check indexed flags
        self.assertTrue(event_abi['inputs'][0]['indexed'])
        self.assertTrue(event_abi['inputs'][1]['indexed'])
        self.assertFalse(event_abi['inputs'][2]['indexed'])
    
    def test_event_signature_computation(self):
        """Test event signature hash computation."""
        code = """
        class Token {
          event Transfer(address from, address to, uint256 amount)
        }
        """
        parser = DafnyParser(code)
        ast = parser.parse()
        
        generator = YulGenerator()
        generator.contract = ast
        generator._compute_event_signatures(ast.events)
        
        # Transfer(address,address,uint256) signature should be computed
        self.assertIn("Transfer", generator.event_signatures)
        sig = generator.event_signatures["Transfer"]
        self.assertTrue(sig.startswith("0x"))
        self.assertEqual(len(sig), 66)  # 0x + 64 hex chars
    
    def test_event_with_no_parameters(self):
        """Test event with no parameters."""
        code = """
        class Contract {
          event Triggered()
          
          method trigger()
            modifies this
          {
            emit Triggered();
          }
        }
        """
        parser = DafnyParser(code)
        ast = parser.parse()
        
        event = ast.events[0]
        self.assertEqual(len(event.params), 0)


if __name__ == '__main__':
    unittest.main()
