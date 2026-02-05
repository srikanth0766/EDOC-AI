"""Test the universal analyzer directly"""
from analyzers.universal_ast_analyzer import UniversalASTAnalyzer

js_code = """
while (true) {
    console.log("loop");
}
"""

analyzer = UniversalASTAnalyzer('javascript')

print("Testing JavaScript infinite loop detection:")
print("=" * 60)

loops = analyzer.find_infinite_loops(js_code)
print(f"\nInfinite loops found: {len(loops)}")
for loop in loops:
    print(f"  - {loop}")

unreachable = analyzer.find_unreachable_code(js_code)
print(f"\nUnreachable code found: {len(unreachable)}")
for code in unreachable:
    print(f"  - {code}")
