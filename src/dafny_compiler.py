from .parser.dafny_parser import DafnyParser
from .translator.yul_generator import YulGenerator
from .compiler.evm_compiler import EVMCompiler
from .compiler.abi_generator import ABIGenerator
from .verifier.dafny_verifier import DafnyVerifier

class DafnyEVMCompiler:
    def __init__(self, solc_path: str = "solc", verify: bool = True, verbose: bool = False):
        self.yul_generator = YulGenerator()
        self.evm_compiler = EVMCompiler(solc_path)
        self.abi_generator = ABIGenerator()
        self.verify_enabled = verify
        self.verbose = verbose
        self.verifier = None
        
        if verify:
            try:
                self.verifier = DafnyVerifier(verbose=verbose)
            except FileNotFoundError:
                self.verify_enabled = False
    
    def compile(self, dafny_source: str, skip_verification: bool = False, verify_only: bool = False) -> dict:
        try:
            # Step 1: Formal verification (if enabled)
            verification_result = None
            if self.verify_enabled and not skip_verification and self.verifier:
                verification_result = self.verifier.verify(dafny_source)
                
                if not verification_result['verified']:
                    return {
                        'success': False,
                        'verified': False,
                        'error': 'Formal verification failed',
                        'verification_errors': verification_result['errors'],
                        'verification_output': verification_result['output']
                    }
                
                # If verify-only mode, return success after verification
                if verify_only:
                    return {
                        'success': True,
                        'verified': True,
                        'verification_output': verification_result['output']
                    }
            
            # Step 2: Parse and compile
            parser = DafnyParser(dafny_source)
            contract_ast = parser.parse()
            
            yul_code = self.yul_generator.generate(contract_ast)
            abi_json = self.abi_generator.generate(contract_ast)
            
            result = self.evm_compiler.compile_and_verify(yul_code)
            
            return {
                'success': result['success'],
                'verified': verification_result['verified'] if verification_result else False,
                'contract_name': contract_ast.name,
                'yul_code': yul_code,
                'abi': abi_json,
                'bytecode': result.get('bytecode', ''),
                'runtime_bytecode': result.get('runtime_bytecode', ''),
                'gas_estimate': result.get('gas_estimate', 0),
                'verification_output': verification_result['output'] if verification_result else None,
                'error': result.get('error')
            }
        
        except Exception as e:
            return {
                'success': False,
                'verified': False,
                'error': str(e)
            }
    
    def compile_file(self, filepath: str, skip_verification: bool = False, verify_only: bool = False) -> dict:
        with open(filepath, 'r') as f:
            source = f.read()
        return self.compile(source, skip_verification, verify_only)
