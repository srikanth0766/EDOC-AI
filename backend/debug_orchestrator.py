"""Debug Orchestrator Logic"""
import sys
from analyzers.control_flow_analyzer import ControlFlowAnalyzer
from analyzers.universal_ast_analyzer import UniversalASTAnalyzer

code = """
while True:
    print("loop")
"""

analyzer = ControlFlowAnalyzer()
print("Analyzing...")
result = analyzer.analyze(code, language='python')
print(f"Has issues: {result.has_issues}")
print(f"Issues type: {type(result.issues)}")
if result.issues:
    print(f"First issue type: {type(result.issues[0])}")
    print(f"First issue content: {result.issues[0]}")

print("Converting to dict...")
try:
    res_dict = result.to_dict()
    print("Conversion successful.")
    print(res_dict)
except Exception as e:
    print(f"Conversion failed: {e}")
    import traceback
    traceback.print_exc()

print("Done.")
