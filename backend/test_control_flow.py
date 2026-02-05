"""
Quick test to verify control flow analysis is working
"""
import requests
import json

# Test with infinite loop code
code = """
while True:
    print("This will run forever!")
    print("No way to exit this loop")
"""

print("Testing control flow analysis...")
print("=" * 60)

response = requests.post(
    "http://localhost:8000/review",
    json={
        "code": code,
        "include_logic_analysis": False,
        "include_optimizations": False,
        "include_control_flow": True
    },
    timeout=15
)

if response.status_code == 200:
    result = response.json()
    
    print("\n✅ Backend Response Received")
    print("\nControl Flow Data:")
    print(f"  Has issues: {result.get('control_flow', {}).get('has_issues', False)}")
    print(f"  Number of issues: {len(result.get('control_flow', {}).get('issues', []))}")
    
    if result.get('control_flow'):
        cf = result['control_flow']
        print(f"\n  Issues found:")
        for issue in cf.get('issues', []):
            print(f"    - {issue['type']}: {issue['description']}")
        
        print(f"\n  Mermaid code generated: {bool(cf.get('mermaid_code'))}")
        if cf.get('mermaid_code'):
            print(f"\n  Mermaid Code Preview (first 200 chars):")
            print(f"  {cf['mermaid_code'][:200]}...")
        else:
            print("\n  ❌ NO MERMAID CODE GENERATED!")
    else:
        print("\n  ❌ NO CONTROL FLOW DATA IN RESPONSE!")
    
    print("\n" + "=" * 60)
    print("Full Response:")
    print(json.dumps(result, indent=2))
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)
