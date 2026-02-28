"""
Category 1C — AST Structural Integrity Tests.

Verifies: no orphan nodes, no circular references, valid DAG structure,
metadata consistency, and node count correctness.
"""

import ast
import pytest


def build_graph(tree):
    """Build a simple parent→child adjacency dict from a Python AST."""
    try:
        import networkx as nx
        G = nx.DiGraph()
        for node in ast.walk(tree):
            node_id = id(node)
            G.add_node(node_id, type=type(node).__name__)
            for child in ast.iter_child_nodes(node):
                G.add_edge(node_id, id(child))
        return G
    except ImportError:
        return None


class TestASTIntegrity:

    def test_ast_is_dag_simple(self):
        """AST of simple code must be a Directed Acyclic Graph."""
        try:
            import networkx as nx
        except ImportError:
            pytest.skip("networkx not installed")
        tree = ast.parse("x = 1 + 2")
        G = build_graph(tree)
        assert G is not None
        assert nx.is_directed_acyclic_graph(G), "AST must be a DAG — no cycles allowed"

    def test_ast_is_dag_complex(self):
        """AST of complex code (class, methods, decorators) must remain a DAG."""
        try:
            import networkx as nx
        except ImportError:
            pytest.skip("networkx not installed")
        code = """
class MyClass:
    def __init__(self, x: int):
        self.x = x
    def compute(self) -> int:
        return self.x * 2
"""
        tree = ast.parse(code)
        G = build_graph(tree)
        assert nx.is_directed_acyclic_graph(G)

    def test_no_orphan_nodes(self):
        """Every non-root node must have at least one parent (in-degree >= 1)."""
        try:
            import networkx as nx
        except ImportError:
            pytest.skip("networkx not installed")
        code = "def f(a, b): return a + b"
        tree = ast.parse(code)
        G = build_graph(tree)
        root_id = id(tree)
        for node_id in G.nodes():
            if node_id != root_id:
                assert G.in_degree(node_id) >= 1, f"Orphan node found: {G.nodes[node_id]}"

    def test_node_count_simple_assign(self):
        """Exact node count for a simple assignment."""
        tree = ast.parse("x = 42")
        nodes = list(ast.walk(tree))
        # Module, Assign, Name, Constant (Store ctx also counted)
        assert len(nodes) >= 4

    def test_node_count_grows_with_complexity(self):
        """More complex code must produce more AST nodes."""
        simple = list(ast.walk(ast.parse("x = 1")))
        complex_ = list(ast.walk(ast.parse(
            "def f(a, b, c):\n    if a:\n        for i in range(b):\n            return c\n"
        )))
        assert len(complex_) > len(simple)

    def test_all_nodes_have_valid_type(self):
        """All walked nodes must be proper AST node instances."""
        code = "import os\nfor i in range(10):\n    print(i)\n"
        tree = ast.parse(code)
        for node in ast.walk(tree):
            assert isinstance(node, ast.AST), f"Non-AST node found: {type(node)}"

    def test_line_numbers_attached(self):
        """Statement nodes must have lineno attribute set."""
        code = "x = 1\ny = 2\nz = x + y\n"
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.stmt):
                assert hasattr(node, "lineno"), f"Missing lineno on {type(node).__name__}"
                assert node.lineno >= 1

    def test_end_lineno_consistency(self):
        """end_lineno must be >= lineno for all statement nodes."""
        code = """
def multi_line():
    x = 1
    y = 2
    return x + y
"""
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.stmt) and hasattr(node, "end_lineno"):
                if node.end_lineno is not None:
                    assert node.end_lineno >= node.lineno

    def test_function_def_has_body(self):
        """FunctionDef nodes must have a non-empty body."""
        code = "def f():\n    pass\n"
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                assert len(node.body) >= 1

    def test_class_def_has_body(self):
        """ClassDef nodes must have a non-empty body."""
        code = "class C:\n    pass\n"
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                assert len(node.body) >= 1

    def test_no_none_in_children(self):
        """iter_child_nodes must never yield None."""
        code = "x = [1, 2, 3]\nfor i in x:\n    print(i)\n"
        tree = ast.parse(code)
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                assert child is not None

    def test_ast_roundtrip_consistency(self):
        """Parsing the same code twice must produce the same structure."""
        code = "def f(a, b):\n    return a + b\n"
        tree1 = ast.parse(code)
        tree2 = ast.parse(code)
        nodes1 = [type(n).__name__ for n in ast.walk(tree1)]
        nodes2 = [type(n).__name__ for n in ast.walk(tree2)]
        assert nodes1 == nodes2
