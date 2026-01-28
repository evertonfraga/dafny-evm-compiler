import re
from typing import List, Optional, Dict, Any
from .dafny_ast import *

class DafnyParser:
    def __init__(self, source: str):
        self.source = source
        self.lines = source.split('\n')
        self.pos = 0
    
    def parse(self) -> Contract:
        contract_name, base_class = self._extract_contract_name()
        imports = self._extract_imports()
        libraries = self._extract_libraries()
        structs = self._extract_structs()
        fields = self._extract_fields()
        constants = self._extract_constants()
        events = self._extract_events()
        errors = self._extract_errors()
        modifiers = self._extract_modifiers()
        constructor = self._extract_constructor()
        methods = self._extract_methods()
        invariants = self._extract_invariants()
        receive_method, fallback_method = self._extract_special_functions(methods)
        
        return Contract(
            name=contract_name,
            fields=fields,
            methods=methods,
            invariants=invariants,
            imports=imports,
            constructor=constructor,
            events=events,
            libraries=libraries,
            structs=structs,
            base_class=base_class,
            modifiers=modifiers,
            errors=errors,
            receive_method=receive_method,
            fallback_method=fallback_method,
            constants=constants
        )
    
    def _extract_contract_name(self) -> tuple[str, Optional[str]]:
        # Try with inheritance: class Derived is Base
        match = re.search(r'class\s+(\w+)\s+is\s+(\w+)', self.source)
        if match:
            return match.group(1), match.group(2)
        # Try without inheritance: class Contract
        match = re.search(r'class\s+(\w+)', self.source)
        return (match.group(1), None) if match else ("Contract", None)
    
    def _extract_imports(self) -> List[str]:
        """Extract import statements (parsing only, not processed)."""
        imports = []
        for line in self.lines:
            # import "path/to/file.dfy"
            if match := re.match(r'\s*import\s+"([^"]+)"', line):
                imports.append(match.group(1))
            # import LibraryName
            elif match := re.match(r'\s*import\s+(\w+)', line):
                imports.append(match.group(1))
        return imports
    
    def _extract_libraries(self) -> List[Library]:
        libraries = []
        for line in self.lines:
            if match := re.match(r'\s*import\s+(\w+)\s+from\s+"([^"]+)"', line):
                libraries.append(Library(match.group(1), match.group(2)))
        return libraries
    
    def _extract_structs(self) -> List[Struct]:
        structs = []
        i = 0
        while i < len(self.lines):
            line = self.lines[i].strip()
            if match := re.match(r'struct\s+(\w+)\s*\{', line):
                name = match.group(1)
                fields = []
                i += 1
                while i < len(self.lines):
                    line = self.lines[i].strip()
                    if line == '}':
                        break
                    if match := re.match(r'(\w+)\s*:\s*(\w+)', line):
                        field_name, type_str = match.groups()
                        fields.append(Variable(field_name, self._parse_type(type_str)))
                    i += 1
                structs.append(Struct(name, fields))
            i += 1
        return structs
    
    def _extract_fields(self) -> List[Variable]:
        fields = []
        in_method = False
        brace_depth = 0
        
        for line in self.lines:
            stripped = line.strip()
            
            # Track if we're inside a method/constructor
            if re.match(r'(method|constructor|function)\s+\w+', stripped):
                in_method = True
                brace_depth = 0
            
            # Track braces to know when we exit method
            if in_method:
                brace_depth += stripped.count('{') - stripped.count('}')
                if brace_depth <= 0 and '}' in stripped:
                    in_method = False
                continue
            
            # Only extract vars at class level (not in methods)
            # Array: public var name: array<type>
            if match := re.match(r'\s*(public\s+)?var\s+(\w+)\s*:\s*array<(\w+)>', line):
                public_prefix, name, elem_type = match.groups()
                is_public = public_prefix is not None
                fields.append(Variable(name, DafnyType(Type.ARRAY, element_type=self._parse_type(elem_type)), 
                                     visibility="public" if is_public else "internal", is_public=is_public))
            # Mapping: public var name: mapping<keyType, valueType>
            elif match := re.match(r'\s*(public\s+)?var\s+(\w+)\s*:\s*mapping<(\w+),\s*(\w+)>', line):
                public_prefix, name, key_type, val_type = match.groups()
                is_public = public_prefix is not None
                fields.append(Variable(name, DafnyType(Type.MAPPING, key_type=self._parse_type(key_type), value_type=self._parse_type(val_type)),
                                     visibility="public" if is_public else "internal", is_public=is_public))
            # Simple type: public var name: type
            elif match := re.match(r'\s*(public\s+)?var\s+(\w+)\s*:\s*(\w+)', line):
                public_prefix, name, type_str = match.groups()
                is_public = public_prefix is not None
                fields.append(Variable(name, self._parse_type(type_str),
                                     visibility="public" if is_public else "internal", is_public=is_public))
        return fields
    
    def _extract_constants(self) -> Dict[str, Any]:
        """Extract ghost constants for verification"""
        constants = {}
        for line in self.lines:
            # ghost const NAME: type := value
            if match := re.match(r'\s*ghost\s+const\s+(\w+)\s*:\s*\w+\s*:=\s*(.+)', line):
                name = match.group(1)
                value_str = match.group(2).strip()
                # Parse the value (simple int/bool for now)
                try:
                    value = int(value_str)
                except ValueError:
                    if value_str.lower() == 'true':
                        value = True
                    elif value_str.lower() == 'false':
                        value = False
                    else:
                        value = value_str
                constants[name] = value
        return constants
    
    def _extract_events(self) -> List[Event]:
        events = []
        for line in self.lines:
            # event Name(type1 indexed param1, type2 param2) anonymous
            if match := re.match(r'\s*event\s+(\w+)\s*\((.*?)\)\s*(anonymous)?', line):
                name = match.group(1)
                params_str = match.group(2)
                anonymous = match.group(3) is not None
                
                # Parse params with indexed markers
                params = []
                indexed = []
                if params_str:
                    for param in params_str.split(','):
                        param = param.strip()
                        # Check for indexed keyword
                        is_indexed = 'indexed' in param
                        param = param.replace('indexed', '').strip()
                        
                        # Parse "name: type" or "type name"
                        if ':' in param:
                            # Dafny style: name: type
                            parts = param.split(':')
                            if len(parts) == 2:
                                name_str = parts[0].strip()
                                type_str = parts[1].strip()
                                params.append(Variable(name_str, self._parse_type(type_str)))
                                indexed.append(is_indexed)
                        else:
                            # Solidity style: type name
                            parts = param.split()
                            if len(parts) >= 2:
                                type_str = parts[0]
                                name_str = parts[1].rstrip(',')
                                params.append(Variable(name_str, self._parse_type(type_str)))
                                indexed.append(is_indexed)
                
                events.append(Event(name, params, indexed, anonymous))
        return events
    
    def _extract_errors(self) -> List[CustomError]:
        errors = []
        for line in self.lines:
            # error Name(type1 param1, type2 param2)
            if match := re.match(r'\s*error\s+(\w+)\s*\((.*?)\)', line):
                name = match.group(1)
                params_str = match.group(2)
                params = []
                if params_str.strip():
                    for param in params_str.split(','):
                        param = param.strip()
                        parts = param.split()
                        if len(parts) >= 2:
                            type_str = parts[0]
                            name_str = parts[1]
                            params.append(Variable(name_str, self._parse_type(type_str)))
                errors.append(CustomError(name, params))
        return errors
    
    def _extract_special_functions(self, methods: List[Method]) -> tuple:
        receive_method = None
        fallback_method = None
        regular_methods = []
        
        for method in methods:
            if method.name == 'receive':
                receive_method = method
            elif method.name == 'fallback':
                fallback_method = method
            else:
                regular_methods.append(method)
        
        # Update methods list to exclude special functions
        methods.clear()
        methods.extend(regular_methods)
        
        return receive_method, fallback_method
    
    def _extract_modifiers(self) -> List[Modifier]:
        modifiers = []
        i = 0
        while i < len(self.lines):
            line = self.lines[i]
            if match := re.match(r'\s*modifier\s+(\w+)\s*\((.*?)\)\s*\{?', line):
                name = match.group(1)
                params_str = match.group(2)
                params = self._parse_params(params_str) if params_str else []
                
                # Extract modifier body
                body = []
                i += 1
                brace_count = 1 if '{' in line else 0
                if brace_count == 0:
                    # Opening brace on next line
                    while i < len(self.lines) and '{' not in self.lines[i]:
                        i += 1
                    if i < len(self.lines):
                        brace_count = 1
                        i += 1
                
                while i < len(self.lines) and brace_count > 0:
                    line = self.lines[i].strip()
                    if '{' in line:
                        brace_count += line.count('{')
                    if '}' in line:
                        brace_count -= line.count('}')
                    if brace_count > 0:
                        # Parse modifier body statements
                        if line and not line.startswith('//'):
                            # For now, store as simple require statements
                            if line.startswith('require'):
                                cond = self._parse_condition(line)
                                if cond:
                                    body.append(Require(cond))
                    i += 1
                
                modifiers.append(Modifier(name, params, body))
            i += 1
        return modifiers
    
    def _extract_constructor(self) -> Optional[Method]:
        """Extract constructor if present"""
        i = 0
        while i < len(self.lines):
            line = self.lines[i]
            match = re.match(r'\s*constructor\s*\((.*?)\)', line)
            if match:
                params_str = match.group(1)
                params = self._parse_params(params_str) if params_str.strip() else []
                
                # Check if opening brace is on same line
                if '{' in line:
                    preconditions, postconditions, body, _ = self._extract_method_body(i + 1, in_body=True)
                else:
                    preconditions, postconditions, body, _ = self._extract_method_body(i + 1, in_body=False)
                
                return Method(
                    name="constructor",
                    params=params,
                    returns=None,
                    preconditions=preconditions,
                    postconditions=postconditions,
                    body=body,
                    is_public=True,
                    is_payable=False,
                    visibility="public",
                    state_mutability="nonpayable",
                    modifiers=[]
                )
            i += 1
        return None
    
    def _extract_methods(self) -> List[Method]:
        methods = []
        i = 0
        while i < len(self.lines):
            line = self.lines[i]
            
            # Parse visibility, state mutability, payable, and modifiers
            visibility = "public"
            state_mutability = None
            is_payable = False
            modifiers = []
            
            # Extract modifiers: public, private, internal, external, view, pure, payable, custom modifiers
            tokens = line.split()
            for token in tokens:
                if token in ['public', 'private', 'internal', 'external']:
                    visibility = token
                elif token in ['view', 'pure']:
                    state_mutability = token
                elif token == 'payable':
                    is_payable = True
                    if state_mutability is None:
                        state_mutability = 'payable'
            
            # Match method signature - use two passes for better parsing
            # First, extract returns clause if present
            returns_str = None
            returns_match = re.search(r'returns\s*\(([^)]+)\)', line)
            if returns_match:
                returns_str = returns_match.group(1)
            
            # Then match the main method signature
            match = re.match(r'\s*(?:(?:public|private|internal|external|view|pure|payable)\s+)*method\s+(\w+)\s*\((.*?)\)', line)
            if match:
                name = match.group(1)
                
                # Reject 'method constructor' - constructors must use 'constructor()' syntax
                if name == "constructor":
                    raise SyntaxError(
                        f"Line {i+1}: Constructor cannot be declared as a method.\n"
                        f"Use 'constructor()' instead of 'method constructor()'.\n"
                        f"Constructors run once during deployment and cannot be called after."
                    )
                params_str = match.group(2)
                
                # Extract modifiers after the closing paren (excluding keywords)
                after_params = line[match.end():]
                modifiers_str = None
                # Find text between ) and { or returns, excluding keywords
                mod_match = re.search(r'\)\s*([^{]*?)(?:returns|\{|$)', line)
                if mod_match:
                    modifiers_str = mod_match.group(1)
                
                # Parse custom modifiers (e.g., "onlyOwner whenNotPaused")
                if modifiers_str:
                    modifiers = [m.strip() for m in modifiers_str.split() if m.strip() and m.strip() not in ['public', 'private', 'internal', 'external', 'view', 'pure', 'payable', 'method', 'returns']]
                
                params = self._parse_params(params_str)
                
                # Parse return values
                ret_type = None
                if returns_str:
                    # Check if multiple returns: "x: uint256, y: bool"
                    if ',' in returns_str:
                        ret_type = self._parse_params(returns_str)
                    else:
                        # Single return: "result: uint256"
                        match_ret = re.match(r'(\w+)\s*:\s*(\w+)', returns_str)
                        if match_ret:
                            # Return as list of Variables for consistency
                            var_name = match_ret.group(1)
                            var_type = self._parse_type(match_ret.group(2))
                            ret_type = [Variable(var_name, var_type)]
                
                # Check if opening brace is on same line
                if '{' in line:
                    preconditions, postconditions, body, i = self._extract_method_body(i + 1, in_body=True)
                else:
                    preconditions, postconditions, body, i = self._extract_method_body(i + 1, in_body=False)
                
                methods.append(Method(
                    name=name,
                    params=params,
                    returns=ret_type,
                    preconditions=preconditions,
                    postconditions=postconditions,
                    body=body,
                    is_public=(visibility == "public"),
                    is_payable=is_payable,
                    visibility=visibility,
                    state_mutability=state_mutability,
                    modifiers=modifiers
                ))
            i += 1
        return methods
    
    def _extract_method_body(self, start: int, in_body: bool = False):
        preconditions = []
        postconditions = []
        body = []
        i = start
        
        while i < len(self.lines):
            line = self.lines[i].strip()
            
            if not in_body:
                if line.startswith('requires'):
                    expr = line.replace('requires', '').strip()
                    # Skip predicate calls like Valid()
                    if not '()' in expr or expr.count('(') > 1:
                        preconditions.append(self._parse_expression(expr))
                elif line.startswith('ensures'):
                    expr = line.replace('ensures', '').strip()
                    # Skip predicate calls
                    if not '()' in expr or expr.count('(') > 1:
                        postconditions.append(self._parse_expression(expr))
                elif line.startswith('modifies'):
                    # Skip modifies clause
                    pass
                elif line == '{':
                    in_body = True
            else:
                if line == '}':
                    break
                if line and not line.startswith('//'):
                    # Check for control flow
                    if line.startswith('if '):
                        stmt, i = self._parse_if_statement(i)
                        if stmt:
                            body.append(stmt)
                        continue
                    elif line.startswith('while '):
                        stmt, i = self._parse_while_loop(i)
                        if stmt:
                            body.append(stmt)
                        continue
                    elif line.startswith('for '):
                        stmt, i = self._parse_for_loop(i)
                        if stmt:
                            body.append(stmt)
                        continue
                    else:
                        stmt = self._parse_statement(line)
                        if stmt:
                            body.append(stmt)
            i += 1
        
        return preconditions, postconditions, body, i
    
    def _parse_params(self, params_str: str) -> List[Variable]:
        if not params_str.strip():
            return []
        params = []
        for param in params_str.split(','):
            match = re.match(r'\s*(\w+)\s*:\s*(\w+)', param)
            if match:
                name, type_str = match.groups()
                params.append(Variable(name, self._parse_type(type_str)))
        return params
    
    def _parse_type(self, type_str: str) -> DafnyType:
        type_map = {
            'int': Type.INT,
            'uint256': Type.UINT256,
            'uint128': Type.UINT128,
            'uint64': Type.UINT64,
            'uint32': Type.UINT32,
            'uint16': Type.UINT16,
            'uint8': Type.UINT8,
            'int256': Type.INT256,
            'int128': Type.INT128,
            'bool': Type.BOOL,
            'address': Type.ADDRESS,
            'string': Type.STRING,
            'bytes': Type.BYTES,
            'bytes32': Type.BYTES32,
        }
        if type_str in type_map:
            return DafnyType(type_map[type_str])
        # Assume it's a struct name
        return DafnyType(Type.STRUCT, struct_name=type_str)
    
    def _parse_statement(self, line: str) -> Optional[Statement]:
        line = line.rstrip(';').strip()
        
        # var name : type := expr
        if match := re.match(r'var\s+(\w+)\s*:\s*(\w+)\s*:=\s*(.+)', line):
            name, type_str, expr = match.groups()
            return VarDecl(
                Variable(name, self._parse_type(type_str)),
                self._parse_expression(expr)
            )
        
        # var name := expr (type inference)
        if match := re.match(r'var\s+(\w+)\s*:=\s*(.+)', line):
            name, expr = match.groups()
            # Use uint256 as default type for type inference
            return VarDecl(
                Variable(name, DafnyType(Type.UINT256)),
                self._parse_expression(expr)
            )
        
        # Array/mapping assignment: name[index] := value or name[i][j] := value
        if '[' in line and ':=' in line:
            # Match pattern: name[...][...] := value
            match = re.match(r'(\w+)((?:\[[^\]]+\])+)\s*:=\s*(.+)', line)
            if match:
                target = match.group(1)
                indices_str = match.group(2)  # All [index] parts
                expr = match.group(3)
                
                # Extract all indices
                indices = []
                for idx_match in re.finditer(r'\[([^\]]+)\]', indices_str):
                    indices.append(self._parse_expression(idx_match.group(1)))
                
                if len(indices) == 1:
                    # Single index: use old format for compatibility
                    return Assignment(target, self._parse_expression(expr), indices[0])
                else:
                    # Multiple indices: use new indices field
                    return Assignment(target, self._parse_expression(expr), indices=indices)
        
        # Struct field assignment: struct.field := value
        if match := re.match(r'(\w+)\.(\w+)\s*:=\s*(.+)', line):
            struct, field, expr = match.groups()
            # Store as special assignment with struct.field as target
            return Assignment(f"{struct}.{field}", self._parse_expression(expr))
        
        # Emit event: emit EventName(args)
        if match := re.match(r'emit\s+(\w+)\((.*)\)', line):
            name, args_str = match.groups()
            args = [self._parse_expression(a.strip()) for a in args_str.split(',')] if args_str.strip() else []
            return EmitEvent(name, args)
        
        # Revert with custom error: revert ErrorName(args)
        if match := re.match(r'revert\s+(\w+)\((.*)\)', line):
            error_name, args_str = match.groups()
            args = [self._parse_expression(a.strip()) for a in args_str.split(',')] if args_str.strip() else []
            return Revert(error_name=error_name, error_args=args)
        
        # Revert with message: revert("message")
        if match := re.match(r'revert\("(.+)"\)', line):
            message = match.group(1)
            return Revert(message=message)
        
        # Revert without args
        if line == 'revert':
            return Revert()
        
        # Selfdestruct: selfdestruct(address)
        if match := re.match(r'selfdestruct\((.+)\)', line):
            recipient = self._parse_expression(match.group(1))
            return Selfdestruct(recipient)
        
        # Array push: arr.push(value)
        if match := re.match(r'(\w+)\.push\((.+)\)', line):
            array, value = match.groups()
            return ArrayPush(array, self._parse_expression(value))
        
        # Array pop: arr.pop()
        if match := re.match(r'(\w+)\.pop\(\)', line):
            return ArrayPop(match.group(1))
        
        if match := re.match(r'(\w+)\s*:=\s*(.+)', line):
            target, expr = match.groups()
            return Assignment(target, self._parse_expression(expr))
        
        if match := re.match(r'return\s+(.+)', line):
            ret_expr = match.group(1)
            # Check for multiple returns: "return x, y;"
            if ',' in ret_expr:
                values = [self._parse_expression(v.strip()) for v in ret_expr.split(',')]
                return Return(values)
            return Return(self._parse_expression(ret_expr))
        
        if match := re.match(r'return\s*', line):
            return Return(None)
        
        if match := re.match(r'assert\s+(.+)', line):
            return Assert(self._parse_expression(match.group(1)))
        
        if match := re.match(r'require\s+(.+)', line):
            return Require(self._parse_expression(match.group(1)))
        
        return None
    
    def _parse_if_statement(self, start: int):
        line = self.lines[start].strip()
        # Match: if condition { or if (condition) {
        match = re.match(r'if\s+(?:\((.+?)\)|(.*?))\s*\{?', line)
        if not match:
            return None, start
        
        # Get condition from either group (with or without parens)
        condition_str = match.group(1) if match.group(1) else match.group(2)
        condition = self._parse_expression(condition_str)
        then_body = []
        else_body = []
        
        i = start + 1
        brace_count = 1
        in_else = False
        
        # Parse blocks
        while i < len(self.lines):
            line = self.lines[i].strip()
            
            # Check for } else { on same line
            if '} else {' in line or line == '} else {':
                in_else = True
                brace_count = 1
                i += 1
                continue
            
            if line == '}':
                brace_count -= 1
                if brace_count == 0:
                    i += 1
                    break
            elif line == '{':
                brace_count += 1
            elif line and not line.startswith('//'):
                stmt = self._parse_statement(line)
                if stmt:
                    if in_else:
                        else_body.append(stmt)
                    else:
                        then_body.append(stmt)
            i += 1
        
        return IfStatement(condition, then_body, else_body if else_body else None), i
    
    def _parse_while_loop(self, start: int):
        line = self.lines[start].strip()
        match = re.match(r'while\s+\((.+?)\)\s*\{?', line)
        if not match:
            return None, start
        
        condition = self._parse_expression(match.group(1))
        body = []
        
        i = start + 1
        brace_count = 1 if '{' in line else 0
        
        while i < len(self.lines):
            line = self.lines[i].strip()
            if line == '}':
                brace_count -= 1
                if brace_count == 0:
                    break
            elif line == '{':
                brace_count += 1
            elif line and not line.startswith('//'):
                stmt = self._parse_statement(line)
                if stmt:
                    body.append(stmt)
            i += 1
        
        return WhileLoop(condition, body), i
    
    def _parse_for_loop(self, start: int):
        line = self.lines[start].strip()
        # for (init; condition; update) { ... }
        match = re.match(r'for\s+\((.+?);(.+?);(.+?)\)\s*\{?', line)
        if not match:
            return None, start
        
        init_str, cond_str, update_str = match.groups()
        init = self._parse_statement(init_str.strip()) if init_str.strip() else None
        condition = self._parse_expression(cond_str.strip())
        update = self._parse_statement(update_str.strip()) if update_str.strip() else None
        
        body = []
        i = start + 1
        brace_count = 1 if '{' in line else 0
        
        while i < len(self.lines):
            line = self.lines[i].strip()
            if line == '}':
                brace_count -= 1
                if brace_count == 0:
                    break
            elif line == '{':
                brace_count += 1
            elif line and not line.startswith('//'):
                stmt = self._parse_statement(line)
                if stmt:
                    body.append(stmt)
            i += 1
        
        return ForLoop(init, condition, update, body), i
    
    def _parse_condition(self, line: str) -> Optional[Expression]:
        """Parse a condition from a require/assert/if statement"""
        # Extract condition from require(condition) or similar
        match = re.search(r'require\s*\((.*?)\)', line)
        if match:
            return self._parse_expression(match.group(1))
        match = re.search(r'assert\s*\((.*?)\)', line)
        if match:
            return self._parse_expression(match.group(1))
        match = re.search(r'if\s*\((.*?)\)', line)
        if match:
            return self._parse_expression(match.group(1))
        return None
    
    def _parse_map_update(self, expr: str):
        """Parse functional map update: map[k := v] or chained map[k1 := v1][k2 := v2]"""
        # Find the base (everything before first '[')
        first_bracket = expr.find('[')
        if first_bracket == -1:
            return None
        
        base = expr[:first_bracket].strip()
        remaining = expr[first_bracket:]
        
        # Parse all [key := value] segments
        updates = []
        i = 0
        while i < len(remaining):
            if remaining[i] == '[':
                # Find matching ']' considering nested brackets
                depth = 1
                j = i + 1
                while j < len(remaining) and depth > 0:
                    if remaining[j] == '[':
                        depth += 1
                    elif remaining[j] == ']':
                        depth -= 1
                    j += 1
                
                # Extract content between brackets
                content = remaining[i+1:j-1]
                
                # Check if this is a map update (contains :=)
                if ':=' in content:
                    # Find := at the correct depth
                    assign_pos = -1
                    depth = 0
                    for k, char in enumerate(content):
                        if char == '[':
                            depth += 1
                        elif char == ']':
                            depth -= 1
                        elif char == ':' and k + 1 < len(content) and content[k+1] == '=' and depth == 0:
                            assign_pos = k
                            break
                    
                    if assign_pos != -1:
                        key = content[:assign_pos].strip()
                        value = content[assign_pos+2:].strip()
                        updates.append((key, value))
                
                i = j
            else:
                i += 1
        
        if not updates:
            return None
        
        # Build nested MapUpdate structure
        # For map[k1 := v1][k2 := v2], create MapUpdate(MapUpdate(base, k1, v1), k2, v2)
        result = MapUpdate(base, self._parse_expression(updates[0][0]), self._parse_expression(updates[0][1]))
        for key, value in updates[1:]:
            result = MapUpdate(result, self._parse_expression(key), self._parse_expression(value))
        
        return result
    
    def _parse_expression(self, expr: str) -> Expression:
        expr = expr.strip()
        
        # Handle parentheses - strip outer parens if balanced
        if expr.startswith('(') and expr.endswith(')'):
            # Check if these are the outermost balanced parens
            depth = 0
            for i, char in enumerate(expr):
                if char == '(':
                    depth += 1
                elif char == ')':
                    depth -= 1
                    if depth == 0 and i == len(expr) - 1:
                        # Outer parens are balanced, strip them
                        return self._parse_expression(expr[1:-1])
        
        # Functional map update: map[key := value] or chained map[k1 := v1][k2 := v2]
        # MUST be checked before binary operators to avoid splitting on operators inside updates
        if '[' in expr and ':=' in expr and ']' in expr:
            map_update = self._parse_map_update(expr)
            if map_update:
                return map_update
        
        # If expression: if condition then thenExpr else elseExpr
        if expr.startswith('if '):
            # Find 'then' and 'else' keywords (not inside nested expressions)
            depth = 0
            then_pos = -1
            else_pos = -1
            i = 3  # Skip 'if '
            
            while i < len(expr):
                if expr[i:i+2] == 'if':
                    depth += 1
                    i += 2
                elif expr[i:i+4] == 'then' and depth == 0 and then_pos == -1:
                    then_pos = i
                    i += 4
                elif expr[i:i+4] == 'else' and depth == 0:
                    else_pos = i
                    break
                else:
                    i += 1
            
            if then_pos > 0 and else_pos > 0:
                condition = expr[3:then_pos].strip()
                then_expr = expr[then_pos+4:else_pos].strip()
                else_expr = expr[else_pos+4:].strip()
                
                return IfExpression(
                    self._parse_expression(condition),
                    self._parse_expression(then_expr),
                    self._parse_expression(else_expr)
                )
        
        # Handle unary operators
        if expr.startswith('!'):
            return UnaryOp('!', self._parse_expression(expr[1:]))
        
        if expr.isdigit():
            return Literal(int(expr), DafnyType(Type.UINT256))
        
        if expr in ('true', 'false'):
            return Literal(expr == 'true', DafnyType(Type.BOOL))
        
        # Binary operators - check before other patterns
        # Parse with proper precedence and parentheses handling
        for op in ['==', '!=', '<=', '>=', '<', '>', '+', '-', '*', '/', '%', '&&', '||', ' in ']:
            # Find operator at depth 0 (not inside parens/brackets)
            depth = 0
            i = 0
            while i < len(expr):
                if expr[i] in '([':
                    depth += 1
                elif expr[i] in ')]':
                    depth -= 1
                elif depth == 0 and expr[i:i+len(op)] == op:
                    # Found operator at top level
                    left = expr[:i].strip()
                    right = expr[i+len(op):].strip()
                    if left and right:  # Make sure both sides exist
                        return BinaryOp(op, self._parse_expression(left), self._parse_expression(right))
                i += 1
        
        # Contract calls: addr.call(data) - check before struct access
        if match := re.match(r'(.+?)\.call\{value:\s*(.+?)\}\((.+?)\)', expr):
            addr, value, data = match.groups()
            return ContractCall(self._parse_expression(addr), 'call', 
                              self._parse_expression(data), self._parse_expression(value))
        if match := re.match(r'(.+?)\.call\((.+?)\)', expr):
            addr, data = match.groups()
            return ContractCall(self._parse_expression(addr), 'call', self._parse_expression(data))
        if match := re.match(r'(.+?)\.(delegatecall|staticcall)\((.+?)\)', expr):
            addr, method, data = match.groups()
            return ContractCall(self._parse_expression(addr), method, self._parse_expression(data))
        
        # Global variables: msg.sender, msg.value, block.timestamp, etc.
        if '.' in expr and not '[' in expr:
            parts = expr.split('.')
            if len(parts) == 2:
                if parts[0] in ('msg', 'block', 'tx'):
                    return GlobalVar(expr)
                # Array length: arr.length
                if parts[1] == 'length':
                    return ArrayLength(parts[0])
                # Struct member access: person.age
                return StructAccess(parts[0], parts[1])
        
        # Array/mapping access: name[index] or nested name[i][j]
        # Match all bracket pairs and build nested structure
        if '[' in expr and ']' in expr:
            # Find base name and all indices
            base_match = re.match(r'(\w+)(\[.+\])+$', expr)
            if base_match:
                base_name = base_match.group(1)
                indices_str = base_match.group(2)
                
                # Extract all [index] parts
                indices = []
                for idx_match in re.finditer(r'\[([^\[\]]+)\]', indices_str):
                    indices.append(idx_match.group(1))
                
                # Build nested ArrayAccess structure
                result = ArrayAccess(base_name, self._parse_expression(indices[0]))
                for idx in indices[1:]:
                    # Wrap previous result in another ArrayAccess
                    result = ArrayAccess(result, self._parse_expression(idx))
                return result
        
        if match := re.match(r'(\w+)\((.*)\)', expr):
            name, args_str = match.groups()
            args = [self._parse_expression(a.strip()) for a in args_str.split(',')] if args_str else []
            return FunctionCall(name, args)
        
        return VarRef(expr)
    
    def _extract_invariants(self) -> List[Expression]:
        invariants = []
        for line in self.lines:
            if match := re.match(r'\s*invariant\s+(.+)', line):
                invariants.append(self._parse_expression(match.group(1)))
        return invariants
