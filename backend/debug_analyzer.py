"""Debug ControlFlowAnalyzer regression directly"""
import ast
import traceback
from analyzers.control_flow_analyzer import ControlFlowAnalyzer

analyzer = ControlFlowAnalyzer()

code = """
while True:
    print("loop")
"""

try:
    print("Analyzing code...")
    result = analyzer.analyze(code, language='python')
    print("Analysis complete.")
    print(f"Has issues: {result.has_issues}")
    if result.has_issues:
        print(f"Issues: {result.issues}")
        print(f"Graph nodes: {len(result.graph_nodes)}")
except Exception:
    traceback.print_exc()
