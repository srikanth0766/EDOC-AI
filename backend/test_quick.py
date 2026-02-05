"""Quick test to see what's being returned"""
import requests
import json

js_code = """
while (true) {
    console.log("loop");
}
"""

response = requests.post(
    "http://localhost:8000/review",
    json={
        "code": js_code,
        "language": "javascript",
        "include_control_flow": True,
        "include_logic_analysis": False,
        "include_optimizations": False
    }
)

print("Status:", response.status_code)
print("\nFull Response:")
print(json.dumps(response.json(), indent=2))
