"""Debug the JavaScript AST"""
import esprima
import json

js_code = """
while (true) {
    console.log("loop");
}
"""

tree = esprima.parseScript(js_code, {'loc': True, 'tolerant': True})
print(json.dumps(tree.toDict(), indent=2))
