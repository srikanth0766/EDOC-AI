"""
Agent orchestrator for comprehensive code review.
Coordinates multiple analysis tools to provide intelligent code feedback.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, asdict, field
from analyzers.compile_checker import CompileTimeChecker, CompileTimeResult
from analyzers.logic_analyzer import LogicAnalyzer
from analyzers.optimization_analyzer import OptimizationAnalyzer
from analyzers.control_flow_analyzer import ControlFlowAnalyzer
from analyzers.smell_detector import SmellDetector
from llm_providers.base import LLMProvider
from llm_providers.factory import create_llm_provider
from model import ErrorDetectionModel


@dataclass
class RuntimeRisk:
    """Represents a runtime error risk."""
    type: str
    line: int
    confidence: float
    explanation: str


@dataclass
class ReviewResult:
    """Complete code review result."""
    compile_time: Dict
    runtime_risks: List[Dict]
    logical_concerns: List[str]
    optimizations: List[Dict]
    control_flow: Optional[Dict]
    summary: str
    smells: List[Dict] = field(default_factory=list)


class CodeReviewAgent:
    """
    Main agentic AI orchestrator for code review.
    
    This agent coordinates multiple analysis tools:
    1. Compile-time checker (AST-based, deterministic)
    2. Runtime error predictor (CodeBERT model)
    3. Logic analyzer (LLM reasoning)
    4. Optimization analyzer (heuristics + LLM)
    """
    
    def __init__(
        self,
        runtime_model: ErrorDetectionModel,
        llm_provider: Optional[LLMProvider] = None
    ):
        """
        Initialize the code review agent.
        
        Args:
            runtime_model: Trained model for runtime error prediction
            llm_provider: Optional LLM provider (created from config if None)
        """
        # Initialize all analyzers
        self.compile_checker = CompileTimeChecker()
        self.runtime_model = runtime_model
        self.control_flow_analyzer = ControlFlowAnalyzer()
        self.smell_detector = SmellDetector()
        
        # Create LLM provider if not provided
        if llm_provider is None:
            try:
                llm_provider = create_llm_provider()
            except Exception as e:
                print(f"Warning: Could not create LLM provider: {e}")
                llm_provider = None
        
        self.llm_provider = llm_provider
        self.logic_analyzer = LogicAnalyzer(llm_provider) if llm_provider else None
        self.optimizer = OptimizationAnalyzer(llm_provider) if llm_provider else None
    
    def review_code(
        self,
        code: str,
        language: str = "python",
        include_logic_analysis: bool = True,
        include_optimizations: bool = True,
        include_control_flow: bool = True
    ) -> ReviewResult:
        """
        Perform comprehensive code review.
        
        This is the main orchestration method that runs all analysis steps.
        
        Args:
            code: Source code to review
            language: Programming language (python, javascript, typescript, etc.)
            include_logic_analysis: Whether to run LLM-based logic analysis
            include_optimizations: Whether to generate optimization suggestions
            include_control_flow: Whether to run control flow analysis
            
        Returns:
            ReviewResult with all analysis results
        """
        # Step 1: Syntax/Compile-time check
        compile_result = None  # Initialize for all languages
        
        if language.lower() == "python":
            # Use Python-specific compile checker
            compile_result = self.compile_checker.check(code)
            compile_dict = self.compile_checker.to_dict(compile_result)
            
            # If compile errors, return early (can't analyze further)
            if compile_result.has_errors:
                return ReviewResult(
                    compile_time=compile_dict,
                    runtime_risks=[],
                    logical_concerns=[],
                    optimizations=[],
                    control_flow=None,
                    summary=f"Found {len(compile_result.errors)} compile-time error(s)"
                )
        else:
            # For non-Python languages, use universal analyzer for syntax check
            from analyzers.universal_ast_analyzer import UniversalASTAnalyzer
            from analyzers.compile_checker import CompileTimeResult, CompileError  # Import for mock object
            
            try:
                analyzer = UniversalASTAnalyzer(language)
                syntax_result = analyzer.check_syntax(code)
                if syntax_result['status'] == 'error':
                    # Convert dict errors to CompileError instances
                    error_objects = [
                        CompileError(
                            type=err.get('type', 'SyntaxError'),
                            line=err.get('line', 0),
                            column=err.get('column', 0),
                            message=err.get('message', 'Syntax error'),
                            suggestion=""  # No suggestions for now
                        )
                        for err in syntax_result['errors']
                    ]
                    
                    compile_dict = {
                        'status': 'error',
                        'errors': syntax_result['errors'],
                        'has_errors': True
                    }
                    # Create mock compile_result for summary generation
                    compile_result = CompileTimeResult(
                        status="error",
                        errors=error_objects  # Use CompileError instances
                    )
                    return ReviewResult(
                        compile_time=compile_dict,
                        runtime_risks=[],
                        logical_concerns=[],
                        optimizations=[],
                        control_flow=None,
                        summary=f"Found {len(syntax_result['errors'])} syntax error(s)"
                    )
                else:
                    compile_dict = {'status': 'valid', 'errors': [], 'has_errors': False}
                    # Create mock compile_result with no errors
                    compile_result = CompileTimeResult(
                        status="ok",
                        errors=[]
                    )
            except ValueError:
                # Language not supported, skip syntax check
                compile_dict = {'status': 'unknown', 'errors': [], 'has_errors': False}
                compile_result = CompileTimeResult(
                    status="ok",
                    errors=[]
                )

        
        # Step 2: Runtime error prediction (your existing model)
        runtime_risks = self._predict_runtime_errors(code)
        
        # Step 3: Logical analysis (LLM reasoning)
        logical_concerns = []
        if include_logic_analysis and self.logic_analyzer:
            logical_concerns = self.logic_analyzer.analyze(code)
        
        # Step 4: Optimization suggestions (heuristics + LLM)
        optimizations = []
        if include_optimizations and self.optimizer:
            optimizations = self.optimizer.suggest(code)
        
        # Step 5: Control flow analysis (visual error explanation)
        control_flow_dict = None
        if include_control_flow:
            control_flow_result = self.control_flow_analyzer.analyze(code, language=language)
            if control_flow_result.has_issues:
                control_flow_dict = control_flow_result.to_dict()
        
        # Step 6: Code smell detection
        smells = []
        try:
            smells = self.smell_detector.detect_to_dict(code)
        except Exception as e:
            print(f"Smell detection error: {e}")

        # Step 7: Generate summary
        summary = self._generate_summary(
            compile_result,
            runtime_risks,
            logical_concerns,
            optimizations,
            smells
        )
        
        return ReviewResult(
            compile_time=compile_dict,
            runtime_risks=[asdict(r) for r in runtime_risks],
            logical_concerns=logical_concerns,
            optimizations=optimizations,
            control_flow=control_flow_dict,
            summary=summary,
            smells=smells
        )
    
    def _predict_runtime_errors(self, code: str) -> List[RuntimeRisk]:
        """
        Predict runtime errors using the CodeBERT model.
        
        Args:
            code: Python source code
            
        Returns:
            List of runtime risks
        """
        try:
            error_type, confidence = self.runtime_model.predict(code)
            
            # Only report if confidence is reasonable and not "Unknown"
            if confidence > 0.3 and error_type != "Unknown":
                # Try to estimate line number (simplified for MVP)
                line = self._estimate_error_line(code, error_type)
                
                explanation = self._explain_runtime_error(error_type)
                
                return [RuntimeRisk(
                    type=error_type,
                    line=line,
                    confidence=round(confidence, 4),
                    explanation=explanation
                )]
            
            return []
        
        except Exception as e:
            print(f"Runtime prediction error: {e}")
            return []
    
    def _estimate_error_line(self, code: str, error_type: str) -> int:
        """
        Estimate which line might cause the error (simplified heuristic).
        
        Args:
            code: Source code
            error_type: Type of error predicted
            
        Returns:
            Estimated line number (0 if unknown)
        """
        lines = code.split('\n')
        
        # Simple heuristics based on error type
        if error_type == "IndexError":
            for i, line in enumerate(lines, 1):
                if '[' in line and ']' in line:
                    return i
        
        elif error_type == "ImportError":
            for i, line in enumerate(lines, 1):
                if 'import' in line:
                    return i
        
        return 0  # Unknown line
    
    def _explain_runtime_error(self, error_type: str) -> str:
        """Generate human-readable explanation for error type."""
        explanations = {
            "IndexError": "Possible array/list index out of bounds",
            "RuntimeError": "Potential runtime error detected",
            "ImportError": "Module import may fail",
            "TypeError": "Type mismatch or invalid operation",
            "ValueError": "Invalid value for operation",
            "AttributeError": "Attribute access may fail",
            "KeyError": "Dictionary key may not exist",
            "ZeroDivisionError": "Possible division by zero"
        }
        return explanations.get(error_type, "Potential runtime issue detected")
    
    def _generate_summary(
        self,
        compile_result: CompileTimeResult,
        runtime_risks: List[RuntimeRisk],
        logical_concerns: List[str],
        optimizations: List[Dict],
        smells: List[Dict] = None
    ) -> str:
        """
        Generate human-readable summary of review.

        Args:
            compile_result: Compile-time check result
            runtime_risks: Runtime error predictions
            logical_concerns: Logical issues found
            optimizations: Optimization suggestions
            smells: Code smells detected

        Returns:
            Summary string
        """
        parts = []
        smells = smells or []

        if compile_result.has_errors:
            parts.append(f"{len(compile_result.errors)} compile-time error(s)")
        else:
            parts.append("✓ No compile-time errors")

        if runtime_risks:
            parts.append(f"{len(runtime_risks)} runtime risk(s)")

        if logical_concerns:
            parts.append(f"{len(logical_concerns)} logical concern(s)")

        if optimizations:
            parts.append(f"{len(optimizations)} optimization(s) available")

        high_conf_smells = [s for s in smells if s.get("confidence", 0) > 0.6]
        if high_conf_smells:
            parts.append(f"{len(high_conf_smells)} code smell(s) detected")

        if not runtime_risks and not logical_concerns and not optimizations and not high_conf_smells:
            return "✓ Code looks good! No issues detected."

        return " | ".join(parts)
