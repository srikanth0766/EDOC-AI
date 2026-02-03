"""
Demo script to showcase the Agentic AI Code Review System.
Tests various code samples to demonstrate all analysis capabilities.
"""

import requests
import json
from typing import Dict

API_URL = "http://localhost:8000/review"

def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")

def review_code(code: str, description: str, include_logic: bool = False, include_opt: bool = True):
    """Send code to API and display results."""
    print(f"📝 {description}")
    print("\nCode:")
    print("-" * 70)
    print(code)
    print("-" * 70)
    
    try:
        response = requests.post(
            API_URL,
            json={
                "code": code,
                "include_logic_analysis": include_logic,
                "include_optimizations": include_opt
            },
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Compile-time results
            print("\n🔍 COMPILE-TIME ANALYSIS:")
            if result["compile_time"]["status"] == "ok":
                print("  ✅ No syntax errors")
            else:
                print("  ❌ Errors found:")
                for err in result["compile_time"]["errors"]:
                    print(f"     Line {err['line']}: {err['type']} - {err['message']}")
                    print(f"     💡 {err['suggestion']}")
            
            # Runtime risks
            print("\n⚠️  RUNTIME RISK ANALYSIS:")
            if result["runtime_risks"]:
                for risk in result["runtime_risks"]:
                    print(f"  • {risk['type']} (confidence: {risk['confidence']:.2%})")
                    print(f"    {risk['explanation']}")
                    if risk['line'] > 0:
                        print(f"    Line: {risk['line']}")
            else:
                print("  ✅ No runtime risks detected")
            
            # Logical concerns
            if include_logic:
                print("\n🧠 LOGICAL ANALYSIS:")
                if result["logical_concerns"]:
                    for concern in result["logical_concerns"]:
                        print(f"  • {concern}")
                else:
                    print("  ✅ No logical concerns")
            
            # Optimizations
            if include_opt:
                print("\n💡 OPTIMIZATION SUGGESTIONS:")
                if result["optimizations"]:
                    for opt in result["optimizations"]:
                        print(f"  • [{opt['type'].upper()}] Line {opt['line']}: {opt['suggestion']}")
                        print(f"    Impact: {opt['impact']}")
                        if opt.get('example'):
                            print(f"    Example: {opt['example']}")
                else:
                    print("  ✅ No optimizations needed")
            
            # Summary
            print(f"\n📊 SUMMARY: {result['summary']}")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    print("\n" + "─" * 70)

# ============================================================================
# DEMO STARTS HERE
# ============================================================================

print_section("🚀 AGENTIC AI CODE REVIEW SYSTEM - DEMO")

print("This demo showcases all four analysis layers:")
print("  1. 🟡 Compile-Time (AST-based syntax checking)")
print("  2. 🔴 Runtime Risks (CodeBERT ML prediction)")
print("  3. 🔵 Logical Concerns (LLM reasoning)")
print("  4. 🟢 Optimizations (Heuristics + LLM)")

# ============================================================================
# TEST 1: Syntax Error
# ============================================================================

print_section("TEST 1: Compile-Time Error Detection")

code1 = """def greet(name)
    return f"Hello {name}"
"""

review_code(code1, "Missing colon in function definition", include_opt=False)

# ============================================================================
# TEST 2: Runtime Error Risk
# ============================================================================

print_section("TEST 2: Runtime Error Prediction")

code2 = """def get_item(items):
    return items[10]  # Potential IndexError
"""

review_code(code2, "Accessing list index without bounds check", include_opt=False)

# ============================================================================
# TEST 3: Optimization Opportunities
# ============================================================================

print_section("TEST 3: Code Optimization Suggestions")

code3 = """def process_items(items):
    for i in range(len(items)):
        print(items[i])
"""

review_code(code3, "Using range(len()) anti-pattern")

# ============================================================================
# TEST 4: Multiple Issues
# ============================================================================

print_section("TEST 4: Multiple Issues Combined")

code4 = """def find_max(numbers):
    max_val = 0
    for i in range(len(numbers)):
        if numbers[i] > max_val:
            max_val = numbers[i]
    return max_val
"""

review_code(code4, "Logic bug + optimization opportunities")

# ============================================================================
# TEST 5: Clean Code
# ============================================================================

print_section("TEST 5: Well-Written Code")

code5 = """def calculate_average(numbers):
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)
"""

review_code(code5, "Properly written function with edge case handling")

# ============================================================================
# TEST 6: Complex Example
# ============================================================================

print_section("TEST 6: Complex Code Analysis")

code6 = """def process_data(data):
    results = []
    for i in range(len(data)):
        if data[i] > 0:
            results.append(data[i] * 2)
    return results
"""

review_code(code6, "List processing with optimization potential")

# ============================================================================
# DEMO COMPLETE
# ============================================================================

print_section("✨ DEMO COMPLETE")

print("The Agentic AI Code Review System successfully demonstrated:")
print("  ✅ Syntax error detection with helpful suggestions")
print("  ✅ Runtime risk prediction using ML")
print("  ✅ Code optimization recommendations")
print("  ✅ Comprehensive multi-layered analysis")
print("\nTo test with LLM-based logical analysis, ensure Ollama is running:")
print("  ollama serve")
print("  ollama pull llama3.2:3b")
print("\nThen set include_logic_analysis=True in the API calls.")
