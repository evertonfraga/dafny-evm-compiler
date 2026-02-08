import subprocess
import tempfile
import os
import re
from pathlib import Path

class DafnyVerifier:
    def __init__(self, dafny_path: str = None, verbose: bool = False):
        self.dafny_path = dafny_path or self._find_dafny()
        self.prelude_path = Path(__file__).parent.parent / 'dafny_prelude.dfy'
        self.verbose = verbose
    
    def _find_dafny(self) -> str:
        """Find Dafny executable"""
        # Check dotnet tools
        home = os.path.expanduser("~")
        dotnet_tool = os.path.join(home, ".dotnet", "tools", "dafny")
        if os.path.exists(dotnet_tool):
            return dotnet_tool
        
        # Check PATH
        try:
            result = subprocess.run(['which', 'dafny'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        raise FileNotFoundError("Dafny not found. Install with: dotnet tool install --global dafny")
    
    def _preprocess_for_verification(self, source: str) -> tuple[str, dict]:
        """
        Preprocess source to make it verifiable by standard Dafny.
        Returns (processed_source, stats)
        """
        stats = {
            'mappings_converted': 0,
            'arrays_converted': 0,
            'types_converted': 0,
            'modifiers_found': [],
            'events_found': []
        }
        
        # Replace mapping<K, V> with map<K, V> (handle nested mappings)
        # Process from innermost to outermost by matching mappings without nested mappings
        mapping_count = 0
        max_iterations = 10  # Prevent infinite loops
        for _ in range(max_iterations):
            # Match mapping<...> where the content doesn't contain 'mapping<'
            match = re.search(r'mapping<([^<>]*(?:<[^<>]*>[^<>]*)*)>', source)
            if not match:
                break
            # Replace this specific match
            full_match = match.group(0)
            inner_content = match.group(1)
            replacement = f'map<{inner_content}>'
            source = source.replace(full_match, replacement, 1)
            mapping_count += 1
        stats['mappings_converted'] = mapping_count
        
        # Replace array<T> with seq<T>
        arrays = re.findall(r'array<([^>]+)>', source)
        stats['arrays_converted'] = len(arrays)
        source = re.sub(r'array<([^>]+)>', r'seq<\1>', source)
        
        # Fix map assignment: balances[key] := value → balances := balances[key := value]
        # This is required because Dafny maps are immutable
        def fix_map_assignment(match):
            indent = match.group(1)
            map_name = match.group(2)
            key = match.group(3)
            value = match.group(4)
            return f"{indent}{map_name} := {map_name}[{key} := {value}];"
        
        source = re.sub(r'^(\s*)(\w+)\[([^\]]+)\]\s*:=\s*([^;]+);', fix_map_assignment, source, flags=re.MULTILINE)
        
        # Count type conversions
        types = ['uint256', 'uint128', 'uint64', 'uint32', 'uint16', 'uint8',
                 'int256', 'int128', 'int64', 'int32', 'int16', 'int8',
                 'address', 'bytes32', 'bytes20', 'bytes4']
        for t in types:
            count = len(re.findall(rf'\b{t}\b', source))
            if count > 0:
                stats['types_converted'] += count
        
        # Replace types
        source = re.sub(r'\buint256\b', 'int', source)
        source = re.sub(r'\buint\d+\b', 'int', source)
        source = re.sub(r'\bint\d+\b', 'int', source)
        source = re.sub(r'\baddress\b', 'int', source)
        source = re.sub(r'\bbytes\d*\b', 'int', source)
        
        # Add variables for EVM globals at class level
        # Find class declaration and inject variables
        def add_evm_vars(match):
            class_decl = match.group(0)
            return class_decl + "\n  var msg_sender: int  // EVM: msg.sender (for verification)"
        source = re.sub(r'class\s+\w+\s*\{', add_evm_vars, source)
        
        # Replace msg.sender with msg_sender
        source = re.sub(r'msg\.sender', 'msg_sender', source)
        
        # Convert class invariants to Valid() predicate pattern
        lines = source.split('\n')
        new_lines = []
        invariants = []
        in_class = False
        class_indent = 0
        added_valid = False
        class_opening_brace_idx = -1
        
        for i, line in enumerate(lines):
            # Check if we're entering a class
            class_match = re.match(r'^(\s*)class\s+\w+', line)
            if class_match:
                in_class = True
                class_indent = len(class_match.group(1))
                invariants = []
                added_valid = False
                new_lines.append(line)
                # Check if opening brace is on same line
                if '{' in line:
                    class_opening_brace_idx = len(new_lines) - 1
            elif in_class:
                # Track opening brace
                if '{' in line and class_opening_brace_idx == -1:
                    class_opening_brace_idx = len(new_lines)
                    new_lines.append(line)
                    continue
                
                # Check if this line is an invariant
                inv_match = re.match(r'^\s*invariant\s+(.+)$', line)
                if inv_match:
                    invariants.append(inv_match.group(1).strip())
                    continue  # Skip adding this line
                
                # Check if we should insert Valid() predicate
                if invariants and not added_valid:
                    # Insert before first var/method/constructor, or after opening brace if nothing else
                    if re.match(r'^\s*(var|method|constructor|function)\s+', line):
                        indent = ' ' * (class_indent + 2)
                        new_lines.append(f'{indent}predicate Valid()')
                        new_lines.append(f'{indent}  reads this')
                        new_lines.append(f'{indent}{{')
                        if len(invariants) == 1:
                            new_lines.append(f'{indent}  {invariants[0]}')
                        else:
                            new_lines.append(f'{indent}  {" && ".join(invariants)}')
                        new_lines.append(f'{indent}}}')
                        new_lines.append('')
                        added_valid = True
                
                # Check if we're exiting the class
                if line.strip():
                    current_indent = len(line) - len(line.lstrip())
                    if current_indent <= class_indent and not line.strip().startswith('//'):
                        # Add Valid() before closing if we haven't added it yet
                        if invariants and not added_valid and re.match(r'^\s*\}', line):
                            indent = ' ' * (class_indent + 2)
                            new_lines.append(f'{indent}predicate Valid()')
                            new_lines.append(f'{indent}  reads this')
                            new_lines.append(f'{indent}{{')
                            if len(invariants) == 1:
                                new_lines.append(f'{indent}  {invariants[0]}')
                            else:
                                new_lines.append(f'{indent}  {" && ".join(invariants)}')
                            new_lines.append(f'{indent}}}')
                            new_lines.append('')
                            added_valid = True
                        in_class = False
                
                new_lines.append(line)
            else:
                new_lines.append(line)
        
        source = '\n'.join(new_lines)
        
        # Add Valid() requires/ensures to methods that modify state
        # This enforces that invariants are maintained
        lines = source.split('\n')
        new_lines = []
        i = 0
        has_valid_predicate = 'predicate Valid()' in source
        
        while i < len(lines):
            line = lines[i]
            # Check if this is a method that modifies this
            if re.match(r'\s*method\s+\w+\(', line) and has_valid_predicate:
                new_lines.append(line)
                # Look ahead to see if it has 'modifies this'
                j = i + 1
                has_modifies_this = False
                has_requires_valid = False
                has_ensures_valid = False
                
                while j < len(lines) and not re.match(r'\s*\{', lines[j]):
                    if 'modifies this' in lines[j] or 'modifies `this' in lines[j]:
                        has_modifies_this = True
                    if 'requires Valid()' in lines[j]:
                        has_requires_valid = True
                    if 'ensures Valid()' in lines[j]:
                        has_ensures_valid = True
                    new_lines.append(lines[j])
                    j += 1
                
                # Add Valid() checks if method modifies this
                if has_modifies_this:
                    indent = '    '
                    if not has_requires_valid:
                        new_lines.append(f'{indent}requires Valid()')
                    if not has_ensures_valid:
                        new_lines.append(f'{indent}ensures Valid()')
                
                i = j
            else:
                new_lines.append(line)
                i += 1
        
        source = '\n'.join(new_lines)
        
        # Convert constructor to init method (Dafny doesn't have constructors in classes)
        # Also ensure it has 'modifies this'
        def convert_constructor(match):
            # Check if modifies clause exists in the next few lines
            return 'method init('
        
        source = re.sub(r'\bconstructor\s*\(', convert_constructor, source)
        
        # Add 'modifies this' and 'ensures Valid()' to init method if not present
        lines = source.split('\n')
        new_lines = []
        i = 0
        has_valid_predicate = 'predicate Valid()' in source
        
        while i < len(lines):
            line = lines[i]
            # Check if this is an init method declaration
            if re.match(r'\s*method init\(', line):
                new_lines.append(line)
                # Look ahead for modifies/ensures clauses or opening brace
                j = i + 1
                has_modifies = False
                has_ensures_valid = False
                
                while j < len(lines) and not re.match(r'\s*\{', lines[j]):
                    if 'modifies' in lines[j]:
                        has_modifies = True
                    if 'ensures Valid()' in lines[j]:
                        has_ensures_valid = True
                    new_lines.append(lines[j])
                    j += 1
                
                # Add missing clauses before the opening brace
                indent = '    '
                if not has_modifies:
                    new_lines.append(f'{indent}modifies this')
                if not has_ensures_valid and has_valid_predicate:
                    new_lines.append(f'{indent}ensures Valid()')
                
                i = j
            else:
                new_lines.append(line)
                i += 1
        source = '\n'.join(new_lines)
        
        # Track modifiers
        modifiers = ['payable', 'view', 'pure', 'external', 'internal']
        for mod in modifiers:
            if re.search(rf'\b{mod}\b', source):
                stats['modifiers_found'].append(mod)
        
        # Model payable: methods that can receive value
        source = re.sub(r'\bpayable\b', '/* payable: can receive ether */', source)
        source = re.sub(r'\bview\b', '/* view: reads only */', source)
        source = re.sub(r'\bpure\b', '/* pure: no state access */', source)
        source = re.sub(r'\bexternal\b', '/* external */', source)
        source = re.sub(r'\binternal\b', '/* internal */', source)
        
        # Track events
        events = re.findall(r'event\s+(\w+)\([^)]*\)', source)
        stats['events_found'] = events
        
        # Model emit: events are observable side effects
        def replace_emit(match):
            event_call = match.group(1)
            return f"/* emit {event_call} */"
        source = re.sub(r'emit\s+(\w+\([^)]*\));?', replace_emit, source)
        
        # Keep event declarations as comments
        source = re.sub(r'event\s+(\w+\([^)]*\));?', r'/* event \1 */', source)
        
        return source, stats
    
    def verify(self, dafny_source: str, include_prelude: bool = False) -> dict:
        """
        Verify Dafny source code using the Dafny verifier.
        
        Args:
            dafny_source: The Dafny source code
            include_prelude: Whether to include EVM type definitions (deprecated)
        
        Returns:
            dict with keys:
                - success: bool
                - verified: bool (True if verification passed)
                - output: str (verifier output)
                - errors: list of error messages
                - stats: dict of preprocessing statistics (if verbose)
        """
        # Preprocess to make verifiable
        processed_source, stats = self._preprocess_for_verification(dafny_source)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dfy', delete=False) as f:
            f.write(processed_source)
            temp_file = f.name
        
        try:
            # Use process group to ensure child processes are killed on timeout
            result = subprocess.run(
                [self.dafny_path, 'verify', 
                 '--resource-limit', '10000000',  # Limit SMT solver resources
                 '--verification-time-limit', '20',  # 20 seconds per method
                 temp_file],
                capture_output=True,
                text=True,
                timeout=30,
                preexec_fn=os.setsid if hasattr(os, 'setsid') else None
            )
            
            output = result.stdout + result.stderr
            verified = result.returncode == 0 and 'verified' in output.lower()
            
            # Parse verification statistics from output
            verification_stats = self._parse_verification_output(output)
            
            errors = []
            if not verified:
                for line in output.split('\n'):
                    if 'error' in line.lower() or 'postcondition' in line.lower() or 'precondition' in line.lower():
                        errors.append(line.strip())
            
            result_dict = {
                'success': True,
                'verified': verified,
                'output': self._format_output(output, stats, verification_stats) if self.verbose else output,
                'errors': errors,
                'return_code': result.returncode
            }
            
            if self.verbose:
                result_dict['preprocessing_stats'] = stats
                result_dict['verification_stats'] = verification_stats
            
            return result_dict
        
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'verified': False,
                'output': '',
                'errors': ['Verification timeout (30s)']
            }
        except Exception as e:
            return {
                'success': False,
                'verified': False,
                'output': '',
                'errors': [str(e)]
            }
        finally:
            try:
                os.unlink(temp_file)
            except:
                pass
    
    def _parse_verification_output(self, output: str) -> dict:
        """Extract verification statistics from Dafny output"""
        stats = {
            'methods_verified': 0,
            'assertions_checked': 0,
            'time_seconds': 0.0
        }
        
        # Parse "Dafny program verifier finished with X verified, Y errors"
        match = re.search(r'(\d+)\s+verified', output)
        if match:
            stats['methods_verified'] = int(match.group(1))
        
        # Parse time if available
        match = re.search(r'(\d+\.?\d*)\s*s', output)
        if match:
            stats['time_seconds'] = float(match.group(1))
        
        return stats
    
    def _format_output(self, output: str, preprocess_stats: dict, verify_stats: dict) -> str:
        """Format verbose output with statistics"""
        formatted = []
        formatted.append("=" * 60)
        formatted.append("FORMAL VERIFICATION REPORT")
        formatted.append("=" * 60)
        
        formatted.append("\n📝 Preprocessing:")
        formatted.append(f"  • Mappings converted: {preprocess_stats['mappings_converted']}")
        formatted.append(f"  • Arrays converted: {preprocess_stats['arrays_converted']}")
        formatted.append(f"  • Types converted: {preprocess_stats['types_converted']}")
        if preprocess_stats['modifiers_found']:
            formatted.append(f"  • Modifiers found: {', '.join(preprocess_stats['modifiers_found'])}")
        if preprocess_stats['events_found']:
            formatted.append(f"  • Events found: {', '.join(preprocess_stats['events_found'])}")
        
        formatted.append("\n✓ Verification Results:")
        formatted.append(f"  • Methods verified: {verify_stats['methods_verified']}")
        if verify_stats['time_seconds'] > 0:
            formatted.append(f"  • Time: {verify_stats['time_seconds']:.2f}s")
        
        formatted.append("\n📄 Dafny Output:")
        formatted.append("-" * 60)
        formatted.append(output)
        formatted.append("-" * 60)
        
        return "\n".join(formatted)
