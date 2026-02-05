"""Test Python to make sure it still works"""
import requests

py_code = """
while True:
    print("loop")
"""

response = requests.post(
    "http://localhost:8000/review",
    json={
        "code": py_code,
        "language": "python",
        "include_control_flow": True,
        "include_logic_analysis": False,
        "include_optimizations": False
    }
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    print(f"Control flow: {result.get('control_flow')}")
else:
    print(f"Error: {response.text}")
