"""
Refactoring rules: maps each code smell to its recommended strategy and prompt template.

All prompts are designed for the existing Ollama LLM provider, but work with any
OpenAI-compatible endpoint. The templates use {code} as the only variable.
"""

from typing import Dict, Any

# Each entry: smell_id -> {strategy, prompt_template, examples}
REFACTOR_RULES: Dict[str, Dict[str, Any]] = {

    "long_method": {
        "strategy": "Extract Method",
        "description": (
            "Break the long method into smaller, well-named sub-methods. "
            "Each sub-method should do one thing and have a clear name that acts as documentation."
        ),
        "prompt_template": (
            "You are a compiler-safe Python refactoring assistant.\n"
            "The following method is too long (Long Method smell). "
            "Refactor it by extracting logical sections into smaller helper methods. "
            "Rules:\n"
            "  1. Do NOT change external behaviour — same inputs must produce same outputs.\n"
            "  2. Use descriptive names for extracted methods.\n"
            "  3. Return ONLY the refactored Python code with no explanation.\n"
            "  4. The refactored code must be syntactically valid Python.\n\n"
            "Code to refactor:\n```python\n{code}\n```\n\n"
            "Refactored code:"
        ),
    },

    "god_class": {
        "strategy": "Split Class",
        "description": (
            "The class has too many responsibilities. "
            "Apply the Single Responsibility Principle — split into smaller classes each with one purpose."
        ),
        "prompt_template": (
            "You are a compiler-safe Python refactoring assistant.\n"
            "The following class has too many methods (God Class smell). "
            "Refactor by splitting it into 2-3 focused classes, each responsible for one concern. "
            "Rules:\n"
            "  1. Do NOT change external behaviour.\n"
            "  2. Give each new class a name that describes its responsibility.\n"
            "  3. Return ONLY the refactored Python code with no explanation.\n"
            "  4. The refactored code must be syntactically valid Python.\n\n"
            "Code to refactor:\n```python\n{code}\n```\n\n"
            "Refactored code:"
        ),
    },

    "feature_envy": {
        "strategy": "Move Method",
        "description": (
            "The method uses data from other classes more than its own. "
            "Consider moving it to the class whose data it uses most."
        ),
        "prompt_template": (
            "You are a compiler-safe Python refactoring assistant.\n"
            "The following method is more interested in another class's data than its own (Feature Envy). "
            "Refactor it so it belongs to the class it uses most. If that's not possible, "
            "reduce external coupling. "
            "Rules:\n"
            "  1. Do NOT change external behaviour.\n"
            "  2. Return ONLY the refactored Python code.\n"
            "  3. The refactored code must be syntactically valid Python.\n\n"
            "Code to refactor:\n```python\n{code}\n```\n\n"
            "Refactored code:"
        ),
    },

    "large_parameter_list": {
        "strategy": "Introduce Parameter Object",
        "description": (
            "Replace the long list of parameters with a single Parameter Object (dataclass or namedtuple)."
        ),
        "prompt_template": (
            "You are a compiler-safe Python refactoring assistant.\n"
            "The following function has too many parameters (Large Parameter List smell). "
            "Introduce a parameter object (Python dataclass) to group related parameters. "
            "Rules:\n"
            "  1. Do NOT change external behaviour.\n"
            "  2. Create a @dataclass to hold the parameters.\n"
            "  3. Return ONLY the refactored Python code with no explanation.\n"
            "  4. The refactored code must be syntactically valid Python.\n\n"
            "Code to refactor:\n```python\n{code}\n```\n\n"
            "Refactored code:"
        ),
    },

    "deep_nesting": {
        "strategy": "Flatten with Early Returns",
        "description": (
            "Reduce nesting by replacing nested if/else with early return guards, "
            "or extract deeply nested blocks into helper methods."
        ),
        "prompt_template": (
            "You are a compiler-safe Python refactoring assistant.\n"
            "The following code has deep nesting (Deep Nesting smell). "
            "Flatten it using early returns or guard clauses. "
            "Rules:\n"
            "  1. Do NOT change external behaviour.\n"
            "  2. Prefer early returns to reduce nesting.\n"
            "  3. Return ONLY the refactored Python code with no explanation.\n"
            "  4. The refactored code must be syntactically valid Python.\n\n"
            "Code to refactor:\n```python\n{code}\n```\n\n"
            "Refactored code:"
        ),
    },

    "high_complexity": {
        "strategy": "Simplify Branching",
        "description": (
            "Reduce cyclomatic complexity by extracting conditions into helper methods, "
            "or using dictionaries / polymorphism instead of long if/elif chains."
        ),
        "prompt_template": (
            "You are a compiler-safe Python refactoring assistant.\n"
            "The following code has high cyclomatic complexity. "
            "Simplify by extracting complex conditions, using lookup tables, or applying polymorphism. "
            "Rules:\n"
            "  1. Do NOT change external behaviour.\n"
            "  2. Return ONLY the refactored Python code with no explanation.\n"
            "  3. The refactored code must be syntactically valid Python.\n\n"
            "Code to refactor:\n```python\n{code}\n```\n\n"
            "Refactored code:"
        ),
    },
}


def get_rule(smell: str) -> Dict[str, Any]:
    """Return refactoring rule for a smell, or a generic fallback."""
    return REFACTOR_RULES.get(smell, {
        "strategy": "General Refactor",
        "description": "Improve code structure and readability.",
        "prompt_template": (
            "You are a Python refactoring assistant.\n"
            "Improve the following code to eliminate the '{smell}' code smell. "
            "Return ONLY the refactored Python code.\n\n"
            "Code:\n```python\n{{code}}\n```\n\n"
            "Refactored code:"
        ).replace("{smell}", smell),
    })
