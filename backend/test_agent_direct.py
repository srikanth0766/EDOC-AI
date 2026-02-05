"""Test the agent orchestrator directly"""
from agent_orchestrator import CodeReviewAgent

agent = CodeReviewAgent()

js_code = """
while (true) {
    console.log("loop");
}
"""

try:
    result = agent.review_code(
        code=js_code,
        language="javascript",
        include_logic_analysis=False,
        include_optimizations=False,
        include_control_flow=True
    )
    print("SUCCESS!")
    print(f"Control flow: {result.control_flow}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
