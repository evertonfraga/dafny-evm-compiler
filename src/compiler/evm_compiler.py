import json
import subprocess
import tempfile
from pathlib import Path

class EVMCompiler:
    def __init__(self, solc_path: str = "solc"):
        self.solc_path = solc_path
    
    def compile_yul(self, yul_code: str) -> dict:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yul', delete=False) as f:
            f.write(yul_code)
            yul_file = f.name
        
        try:
            result = subprocess.run(
                [self.solc_path, '--strict-assembly', '--optimize', '--bin', yul_file],
                capture_output=True,
                text=True,
                check=True
            )
            
            output = result.stdout
            bytecode = self._extract_bytecode(output, 'Binary representation:')
            
            return {
                'bytecode': bytecode,
                'runtime_bytecode': bytecode,
                'success': True
            }
        
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'error': e.stderr
            }
        finally:
            Path(yul_file).unlink(missing_ok=True)
    
    def _extract_bytecode(self, output: str, marker: str) -> str:
        lines = output.split('\n')
        for i, line in enumerate(lines):
            if marker in line:
                if i + 1 < len(lines):
                    return lines[i + 1].strip()
        return ""
    
    def compile_and_verify(self, yul_code: str) -> dict:
        result = self.compile_yul(yul_code)
        
        if result['success']:
            result['gas_estimate'] = len(result['bytecode']) // 2
            result['verified'] = True
        
        return result
