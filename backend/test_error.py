"""Test with better error output"""
import requests

js_code = """
while (true) {
    console.log("loop");
}
"""

try:
    response = requests.post(
        "http://localhost:8000/review",
        json={
            "code": js_code,
            "language": "javascript",
            "include_control_flow": True,
            "include_logic_analysis": False,
            "include_optimizations": False
        },
        timeout=30
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()
