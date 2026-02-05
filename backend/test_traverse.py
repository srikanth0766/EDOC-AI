"""Debug the JavaScript infinite loop detection"""
import esprima

js_code = """
while (true) {
    console.log("loop");
}
"""

tree = esprima.parseScript(js_code, {'loc': True, 'tolerant': True})

def traverse(node, depth=0):
    """Recursively traverse AST"""
    if not isinstance(node, dict):
        return
    
    node_type = node.get('type')
    indent = "  " * depth
    print(f"{indent}{node_type}")
    
    # Check for while(true) loops
    if node_type == 'WhileStatement':
        test = node.get('test', {})
        print(f"{indent}  Test type: {test.get('type')}")
        print(f"{indent}  Test value: {test.get('value')}")
        print(f"{indent}  Test value type: {type(test.get('value'))}")
        print(f"{indent}  Is True? {test.get('value') is True}")
        print(f"{indent}  == True? {test.get('value') == True}")
    
    # Traverse children
    for key, value in node.items():
        if isinstance(value, dict):
            traverse(value, depth + 1)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    traverse(item, depth + 1)

traverse(tree.toDict())
