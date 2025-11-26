import unittest
from src.parser.dafny_parser import DafnyParser
from src.translator.yul_generator import YulGenerator
from src.dafny_compiler import DafnyEVMCompiler

class TestModifiers(unittest.TestCase):
    def test_parse_modifier(self):
        """Test parsing of custom modifiers"""
        source = """
        class Test {
          var owner: address
          
          modifier onlyOwner() {
            require(msg.sender == owner);
          }
        }
        """
        parser = DafnyParser(source)
        contract = parser.parse()
        
        self.assertEqual(len(contract.modifiers), 1)
        self.assertEqual(contract.modifiers[0].name, "onlyOwner")
        self.assertEqual(len(contract.modifiers[0].body), 1)
    
    def test_method_with_modifier(self):
        """Test method with custom modifier"""
        source = """
        class Test {
          var owner: address
          
          modifier onlyOwner() {
            require(msg.sender == owner);
          }
          
          method restricted() onlyOwner {
            owner := msg.sender;
          }
        }
        """
        parser = DafnyParser(source)
        contract = parser.parse()
        
        self.assertEqual(len(contract.methods), 1)
        self.assertIn("onlyOwner", contract.methods[0].modifiers)
    
    def test_modifier_compilation(self):
        """Test that modifiers are compiled into Yul"""
        source = """
        class Test {
          var owner: address
          
          modifier onlyOwner() {
            require(msg.sender == owner);
          }
          
          method setOwner(newOwner: address) onlyOwner {
            owner := newOwner;
          }
        }
        """
        compiler = DafnyEVMCompiler(verify=False)
        result = compiler.compile(source)
        
        self.assertTrue(result['success'])
        if 'yul' in result:
            yul = result['yul']
            # Check that modifier check is injected
            self.assertIn('caller()', yul)
            self.assertIn('sload(0)', yul)
            self.assertIn('eq(', yul)
    
    def test_multiple_modifiers(self):
        """Test method with multiple modifiers"""
        source = """
        class Test {
          var owner: address
          var paused: bool
          
          modifier onlyOwner() {
            require(msg.sender == owner);
          }
          
          modifier whenNotPaused() {
            require(!paused);
          }
          
          method restricted() onlyOwner whenNotPaused {
            owner := msg.sender;
          }
        }
        """
        parser = DafnyParser(source)
        contract = parser.parse()
        
        self.assertEqual(len(contract.modifiers), 2)
        self.assertEqual(len(contract.methods[0].modifiers), 2)
        self.assertIn("onlyOwner", contract.methods[0].modifiers)
        self.assertIn("whenNotPaused", contract.methods[0].modifiers)

class TestVisibility(unittest.TestCase):
    def test_parse_public_method(self):
        """Test parsing public visibility"""
        source = """
        class Test {
          method publicMethod() public {
            var x: uint256 := 1;
          }
        }
        """
        parser = DafnyParser(source)
        contract = parser.parse()
        
        self.assertEqual(contract.methods[0].visibility, "public")
    
    def test_parse_private_method(self):
        """Test parsing private visibility"""
        source = """
        class Test {
          method privateMethod() private {
            var x: uint256 := 1;
          }
        }
        """
        parser = DafnyParser(source)
        contract = parser.parse()
        
        self.assertEqual(contract.methods[0].visibility, "private")
    
    def test_parse_internal_method(self):
        """Test parsing internal visibility"""
        source = """
        class Test {
          method internalMethod() internal {
            var x: uint256 := 1;
          }
        }
        """
        parser = DafnyParser(source)
        contract = parser.parse()
        
        self.assertEqual(contract.methods[0].visibility, "internal")
    
    def test_parse_external_method(self):
        """Test parsing external visibility"""
        source = """
        class Test {
          method externalMethod() external {
            var x: uint256 := 1;
          }
        }
        """
        parser = DafnyParser(source)
        contract = parser.parse()
        
        self.assertEqual(contract.methods[0].visibility, "external")

class TestStateMutability(unittest.TestCase):
    def test_parse_view_method(self):
        """Test parsing view state mutability"""
        source = """
        class Test {
          var value: uint256
          
          method getValue() view returns (v: uint256) {
            return value;
          }
        }
        """
        parser = DafnyParser(source)
        contract = parser.parse()
        
        self.assertEqual(contract.methods[0].state_mutability, "view")
    
    def test_parse_pure_method(self):
        """Test parsing pure state mutability"""
        source = """
        class Test {
          method add(a: uint256, b: uint256) pure returns (result: uint256) {
            return a + b;
          }
        }
        """
        parser = DafnyParser(source)
        contract = parser.parse()
        
        self.assertEqual(contract.methods[0].state_mutability, "pure")
    
    def test_parse_payable_method(self):
        """Test parsing payable state mutability"""
        source = """
        class Test {
          payable method deposit() {
            var x: uint256 := msg.value;
          }
        }
        """
        parser = DafnyParser(source)
        contract = parser.parse()
        
        self.assertTrue(contract.methods[0].is_payable)
        self.assertEqual(contract.methods[0].state_mutability, "payable")

class TestInheritance(unittest.TestCase):
    def test_parse_inheritance(self):
        """Test parsing contract inheritance"""
        source = """
        class Derived is Base {
          var y: uint256
        }
        """
        parser = DafnyParser(source)
        contract = parser.parse()
        
        self.assertEqual(contract.name, "Derived")
        self.assertEqual(contract.base_class, "Base")
    
    def test_no_inheritance(self):
        """Test parsing contract without inheritance"""
        source = """
        class Simple {
          var x: uint256
        }
        """
        parser = DafnyParser(source)
        contract = parser.parse()
        
        self.assertEqual(contract.name, "Simple")
        self.assertIsNone(contract.base_class)

if __name__ == '__main__':
    unittest.main()
