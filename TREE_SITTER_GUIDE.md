# Multi-Language AST Parsing Options

## Current Setup
- **Python**: Using Python's built-in `ast` module ✅
- **Other languages**: Not supported ❌

---

## 🔍 AST Parser Options for Each Language

### Option A: Language-Specific Parsers (Best Accuracy)

Each language has its own parser library:

| Language | Python Library | Installation | Accuracy |
|----------|---------------|--------------|----------|
| **JavaScript/TypeScript** | `esprima` or `acorn` (via Node) | `npm install esprima` | ⭐⭐⭐⭐⭐ |
| **JavaScript** | `pyjsparser` | `pip install pyjsparser` | ⭐⭐⭐⭐ |
| **Java** | `javalang` | `pip install javalang` | ⭐⭐⭐⭐ |
| **C/C++** | `pycparser` | `pip install pycparser` | ⭐⭐⭐⭐ |
| **Go** | `tree-sitter` | `pip install tree-sitter` | ⭐⭐⭐⭐⭐ |

---

### Option B: Universal Parser - Tree-sitter ⭐ RECOMMENDED

**Tree-sitter** is a universal parser that supports 40+ languages!

#### What is Tree-sitter?
- Universal parsing library
- Used by GitHub, Atom, Neovim
- Supports: Python, JavaScript, TypeScript, Java, C++, Go, Rust, Ruby, PHP, etc.
- **One library for ALL languages**

#### Installation:
```bash
pip install tree-sitter
pip install tree-sitter-languages  # Pre-built parsers for 40+ languages
```

#### Example Usage:
```python
from tree_sitter_languages import get_parser

# Automatically detect and parse any language
parser = get_parser('javascript')
tree = parser.parse(bytes(code, 'utf8'))

# Same API for all languages!
parser_python = get_parser('python')
parser_java = get_parser('java')
parser_cpp = get_parser('cpp')
```

---

### Option C: Universal AST - LibCST / AST Unification

**LibCST** (for Python) and similar tools provide a unified AST interface.

---

## 🚀 Recommended Architecture with Tree-sitter

### New File Structure:
```
backend/
├── analyzers/
│   ├── universal_ast_analyzer.py  # NEW - Uses tree-sitter
│   ├── compile_checker.py         # OLD - Python only
│   └── control_flow_analyzer.py   # UPDATE - Use tree-sitter
```

### Implementation:

#### 1. Universal AST Analyzer
```python
# backend/analyzers/universal_ast_analyzer.py

from tree_sitter_languages import get_parser, get_language
from typing import List, Optional

class UniversalASTAnalyzer:
    """
    Universal code analyzer using Tree-sitter.
    Supports 40+ programming languages with a single API.
    """
    
    SUPPORTED_LANGUAGES = {
        'python': 'python',
        'javascript': 'javascript',
        'typescript': 'typescript',
        'javascriptreact': 'tsx',  # JSX
        'typescriptreact': 'tsx',
        'java': 'java',
        'cpp': 'cpp',
        'c': 'c',
        'go': 'go',
        'rust': 'rust',
        'ruby': 'ruby',
        'php': 'php'
    }
    
    def __init__(self, language: str):
        """Initialize parser for specific language"""
        lang_key = self.SUPPORTED_LANGUAGES.get(language.lower())
        if not lang_key:
            raise ValueError(f"Language {language} not supported")
        
        self.language = language
        self.parser = get_parser(lang_key)
        self.lang_obj = get_language(lang_key)
    
    def parse(self, code: str):
        """Parse code into AST"""
        tree = self.parser.parse(bytes(code, 'utf8'))
        return tree.root_node
    
    def check_syntax(self, code: str) -> dict:
        """Check for syntax errors"""
        tree = self.parser.parse(bytes(code, 'utf8'))
        root = tree.root_node
        
        errors = []
        if root.has_error:
            # Find error nodes
            errors = self._find_errors(root)
        
        return {
            'status': 'error' if errors else 'valid',
            'errors': errors
        }
    
    def _find_errors(self, node, errors=None):
        """Recursively find error nodes in AST"""
        if errors is None:
            errors = []
        
        if node.type == 'ERROR':
            errors.append({
                'line': node.start_point[0] + 1,
                'column': node.start_point[1],
                'message': f'Syntax error at line {node.start_point[0] + 1}',
                'type': 'SyntaxError'
            })
        
        for child in node.children:
            self._find_errors(child, errors)
        
        return errors
    
    def find_loops(self, code: str) -> List[dict]:
        """Find all loop structures (while, for, etc.)"""
        root = self.parse(code)
        loops = []
        
        # Language-specific loop node types
        loop_types = {
            'python': ['while_statement', 'for_statement'],
            'javascript': ['while_statement', 'for_statement', 'for_in_statement', 'for_of_statement'],
            'java': ['while_statement', 'for_statement', 'enhanced_for_statement'],
            'cpp': ['while_statement', 'for_statement', 'do_statement'],
        }
        
        target_types = loop_types.get(self.language, ['while_statement', 'for_statement'])
        
        def traverse(node):
            if node.type in target_types:
                loops.append({
                    'type': node.type,
                    'line': node.start_point[0] + 1,
                    'text': node.text.decode('utf8')
                })
            
            for child in node.children:
                traverse(child)
        
        traverse(root)
        return loops
    
    def find_infinite_loops(self, code: str) -> List[dict]:
        """Detect infinite loop patterns"""
        root = self.parse(code)
        issues = []
        
        def traverse(node):
            # Pattern: while(true) or while True
            if node.type == 'while_statement':
                condition = node.child_by_field_name('condition')
                if condition:
                    cond_text = condition.text.decode('utf8').lower()
                    if cond_text in ['true', '(true)', '1', '(1)']:
                        # Check if there's a break statement
                        body = node.child_by_field_name('body')
                        has_break = self._has_break_statement(body)
                        
                        if not has_break:
                            issues.append({
                                'type': 'infinite_loop',
                                'line': node.start_point[0] + 1,
                                'description': f'Infinite loop: while(true) without break',
                                'severity': 'error'
                            })
            
            for child in node.children:
                traverse(child)
        
        traverse(root)
        return issues
    
    def _has_break_statement(self, node) -> bool:
        """Check if node contains a break statement"""
        if not node:
            return False
        
        if node.type in ['break_statement', 'return_statement']:
            return True
        
        for child in node.children:
            if self._has_break_statement(child):
                return True
        
        return False
```

#### 2. Updated Control Flow Analyzer
```python
# backend/analyzers/control_flow_analyzer.py

from analyzers.universal_ast_analyzer import UniversalASTAnalyzer

class ControlFlowAnalyzer:
    def analyze(self, code: str, language: str = "python"):
        """Analyze control flow for any language using Tree-sitter"""
        
        try:
            analyzer = UniversalASTAnalyzer(language)
            
            # Find infinite loops
            infinite_loops = analyzer.find_infinite_loops(code)
            
            # Find unreachable code
            unreachable = self._find_unreachable_code(analyzer, code)
            
            # Combine issues
            issues = infinite_loops + unreachable
            
            # Generate visualization
            if issues:
                nodes, edges = self._generate_graph(issues[0], code, language)
                mermaid = self._generate_mermaid(nodes, edges)
            else:
                nodes, edges, mermaid = [], [], ""
            
            return ControlFlowResult(
                has_issues=len(issues) > 0,
                issues=issues,
                graph_nodes=nodes,
                graph_edges=edges,
                mermaid_code=mermaid
            )
        
        except ValueError as e:
            # Language not supported, fall back to LLM
            return self._analyze_with_llm(code, language)
```

---

## 📦 Installation & Setup

### Step 1: Install Tree-sitter
```bash
cd backend
pip install tree-sitter tree-sitter-languages
```

### Step 2: Test It
```python
# test_tree_sitter.py
from tree_sitter_languages import get_parser

# Test JavaScript
js_code = """
while (true) {
    console.log("infinite!");
}
"""

parser = get_parser('javascript')
tree = parser.parse(bytes(js_code, 'utf8'))
print(f"Parsed successfully: {not tree.root_node.has_error}")

# Test Python
py_code = """
while True:
    print("infinite!")
"""

parser = get_parser('python')
tree = parser.parse(bytes(py_code, 'utf8'))
print(f"Parsed successfully: {not tree.root_node.has_error}")
```

---

## 🎯 Benefits of Tree-sitter Approach

### ✅ Advantages:
1. **One library for all languages** - No need for language-specific parsers
2. **40+ languages supported** - Python, JS, TS, Java, C++, Go, Rust, etc.
3. **Fast and accurate** - Used by GitHub and major editors
4. **Consistent API** - Same code works for all languages
5. **Incremental parsing** - Fast for large files
6. **Error recovery** - Can parse incomplete code

### ❌ Disadvantages:
1. **Learning curve** - Different from Python's `ast` module
2. **Node types vary** - Each language has different node names
3. **Installation size** - ~50MB for all language grammars

---

## 🔄 Migration Strategy

### Phase 1: Add Tree-sitter (Parallel)
- Keep existing Python `ast` analyzer
- Add new `UniversalASTAnalyzer` for other languages
- Use tree-sitter for JS/TS/Java/C++

### Phase 2: Unify (Optional)
- Migrate Python analysis to tree-sitter too
- Remove old `ast`-based code
- Single analyzer for all languages

---

## 💡 Recommended Approach

**Use Tree-sitter for multi-language AST parsing!**

### Why:
- ✅ Industry standard (GitHub, Atom, Neovim use it)
- ✅ Supports 40+ languages out of the box
- ✅ One API for all languages
- ✅ Fast and reliable
- ✅ Active development

### Implementation Time:
- **Setup**: 30 minutes
- **Universal analyzer**: 2-3 hours
- **Control flow for JS/TS**: 2-3 hours
- **Testing**: 1 hour

**Total**: ~6-8 hours for full multi-language AST support

---

## 🚀 Next Steps

**Should I implement this?**

1. ✅ Install tree-sitter
2. ✅ Create `UniversalASTAnalyzer`
3. ✅ Update `ControlFlowAnalyzer` to use it
4. ✅ Test with JavaScript/TypeScript
5. ✅ Add support for Java, C++, etc.

**This gives you the BEST of both worlds:**
- Accurate AST-based analysis (like Python)
- Support for multiple languages
- One unified codebase

Let me know if you want me to implement this! 🎯
