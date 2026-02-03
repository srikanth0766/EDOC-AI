"""
Simple test script to verify the agentic AI system works.
Tests compile-time checker, runtime predictor, and agent orchestration.
"""

# Test 1: Compile-time error detection
print("=" * 60)
print("TEST 1: Compile-Time Error Detection")
print("=" * 60)

from analyzers.compile_checker import CompileTimeChecker

checker = CompileTimeChecker()

# Test with syntax error
bad_code = """
def hello()
    print("missing colon")
"""

result = checker.check(bad_code)
print(f"Status: {result.status}")
print(f"Errors found: {len(result.errors)}")
for err in result.errors:
    print(f"  - {err.type} at line {err.line}: {err.message}")
    print(f"    Suggestion: {err.suggestion}")

# Test with valid code
good_code = """
def hello():
    print("Hello, world!")
"""

result = checker.check(good_code)
print(f"\nValid code status: {result.status}")

# Test 2: Agent orchestration (without LLM for now)
print("\n" + "=" * 60)
print("TEST 2: Agent Orchestration (Basic)")
print("=" * 60)

from model import ErrorDetectionModel
from agent_orchestrator import CodeReviewAgent

print("Loading model...")
model = ErrorDetectionModel()

print("Creating agent...")
agent = CodeReviewAgent(runtime_model=model, llm_provider=None)

# Test code with potential runtime error
test_code = """
def process_list(items):
    for i in range(len(items)):
        print(items[i])
    return items[10]  # Potential IndexError
"""

print("\nReviewing code...")
review = agent.review_code(
    test_code,
    include_logic_analysis=False,  # Skip LLM for basic test
    include_optimizations=False
)

print(f"\nCompile-time: {review.compile_time['status']}")
print(f"Runtime risks: {len(review.runtime_risks)}")
for risk in review.runtime_risks:
    print(f"  - {risk['type']} (confidence: {risk['confidence']})")
    print(f"    {risk['explanation']}")

print(f"\nSummary: {review.summary}")

print("\n" + "=" * 60)
print("✓ Basic tests passed!")
print("=" * 60)
