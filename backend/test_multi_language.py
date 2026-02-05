"""
Test script to verify multi-language support works correctly.
Tests JavaScript infinite loop detection via the API.
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"

# Test 1: JavaScript Infinite Loop
print("=" * 60)
print("TEST 1: JavaScript Infinite Loop Detection")
print("=" * 60)

js_infinite_loop = """
while (true) {
    console.log("This will run forever!");
    console.log("No way to exit this loop");
}
"""

try:
    response = requests.post(
        f"{BACKEND_URL}/review",
        json={
            "code": js_infinite_loop,
            "language": "javascript",
            "include_logic_analysis": False,
            "include_optimizations": False,
            "include_control_flow": True
        },
        timeout=15
    )
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ SUCCESS: Backend responded")
        
        # Check control flow
        if result.get('control_flow'):
            cf = result['control_flow']
            print(f"\n📊 Control Flow Analysis:")
            print(f"  Has issues: {cf.get('has_issues')}")
            print(f"  Number of issues: {len(cf.get('issues', []))}")
            
            if cf.get('issues'):
                print(f"\n  Issues found:")
                for issue in cf['issues']:
                    print(f"    - Line {issue['line']}: {issue['description']}")
            
            if cf.get('mermaid_code'):
                print(f"\n  ✅ Mermaid diagram generated!")
                print(f"  Preview (first 200 chars):")
                print(f"  {cf['mermaid_code'][:200]}...")
            else:
                print(f"\n  ❌ NO MERMAID CODE!")
        else:
            print("\n❌ NO CONTROL FLOW DATA!")
    else:
        print(f"\n❌ ERROR: {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"\n❌ EXCEPTION: {e}")

# Test 2: JavaScript Unreachable Code
print("\n\n" + "=" * 60)
print("TEST 2: JavaScript Unreachable Code Detection")
print("=" * 60)

js_unreachable = """
function calculate() {
    const x = 10;
    return x + 20;
    console.log("This line will never execute");
    const y = 5;
}
"""

try:
    response = requests.post(
        f"{BACKEND_URL}/review",
        json={
            "code": js_unreachable,
            "language": "javascript",
            "include_logic_analysis": False,
            "include_optimizations": False,
            "include_control_flow": True
        },
        timeout=15
    )
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ SUCCESS: Backend responded")
        
        if result.get('control_flow'):
            cf = result['control_flow']
            print(f"\n📊 Control Flow Analysis:")
            print(f"  Has issues: {cf.get('has_issues')}")
            
            if cf.get('issues'):
                print(f"\n  Issues found:")
                for issue in cf['issues']:
                    print(f"    - Line {issue['line']}: {issue['description']}")
            else:
                print(f"\n  ℹ️  No issues found")
        else:
            print("\n❌ NO CONTROL FLOW DATA!")
    else:
        print(f"\n❌ ERROR: {response.status_code}")

except Exception as e:
    print(f"\n❌ EXCEPTION: {e}")

# Test 3: Python (Regression Test)
print("\n\n" + "=" * 60)
print("TEST 3: Python Infinite Loop (Regression Test)")
print("=" * 60)

py_infinite_loop = """
while True:
    print("This will run forever!")
"""

try:
    response = requests.post(
        f"{BACKEND_URL}/review",
        json={
            "code": py_infinite_loop,
            "language": "python",
            "include_logic_analysis": False,
            "include_optimizations": False,
            "include_control_flow": True
        },
        timeout=15
    )
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ SUCCESS: Python still works!")
        
        if result.get('control_flow') and result['control_flow'].get('has_issues'):
            print(f"  ✅ Infinite loop detected in Python code")
        else:
            print(f"  ❌ Failed to detect Python infinite loop")
    else:
        print(f"\n❌ ERROR: {response.status_code}")

except Exception as e:
    print(f"\n❌ EXCEPTION: {e}")

print("\n\n" + "=" * 60)
print("TESTING COMPLETE")
print("=" * 60)
