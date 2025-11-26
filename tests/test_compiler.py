import unittest
from src.dafny_compiler import DafnyEVMCompiler
from src.parser.dafny_parser import DafnyParser
from src.translator.yul_generator import YulGenerator

def get_test_compiler():
    return DafnyEVMCompiler(verify=False)

class TestDafnyParser(unittest.TestCase):
    def test_parse_simple_contract(self):
        source = """
        class Counter {
          var count: uint256
          
          method increment()
            requires count < 1000
            ensures count == old(count) + 1
          {
            count := count + 1;
          }
        }
        """
        parser = DafnyParser(source)
        contract = parser.parse()
        
        self.assertEqual(contract.name, "Counter")
        self.assertEqual(len(contract.fields), 1)
        self.assertEqual(contract.fields[0].name, "count")
        self.assertEqual(len(contract.methods), 1)
        self.assertEqual(contract.methods[0].name, "increment")

class TestYulGenerator(unittest.TestCase):
    def test_generate_simple_method(self):
        source = """
        class Simple {
          method getValue() returns (v: uint256) {
            return 42;
          }
        }
        """
        parser = DafnyParser(source)
        contract = parser.parse()
        generator = YulGenerator()
        yul = generator.generate(contract)
        
        self.assertIn("object \"Simple\"", yul)
        self.assertIn("function getValue()", yul)
        self.assertIn("return(0, 32)", yul)

class TestEndToEnd(unittest.TestCase):
    def test_compile_simple_contract(self):
        source = """
        class Test {
          var value: uint256
          
          method setValue(v: uint256) {
            value := v;
          }
          
          method getValue() returns (result: uint256) {
            return value;
          }
        }
        """
        compiler = get_test_compiler()
        result = compiler.compile(source)
        
        self.assertTrue(result['success'], f"Compilation failed: {result.get('error')}")
        self.assertIn('bytecode', result)
        self.assertIn('yul_code', result)
        self.assertGreater(len(result['bytecode']), 0)

if __name__ == '__main__':
    unittest.main()
