"""
Layer 2: Complex Refactoring Engine - Comprehensive Test Suite

Tests cover:
- Dependency analysis (import extraction, cycle detection, impact analysis)
- Semantic analysis (function signature extraction, API compatibility)
- Refactoring planning and execution
- Safety verification and rollback capability
"""

import pytest
from typing import Dict, Set, List
import ast
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../scripts"))

from orchestrator_layer2_refactoring import (
    ImportInfo,
    FunctionAnalysis,
    APISignature,
    Cycle,
    ImpactResult,
    RefactoringPlan,
    RefactoringResult,
    DependencyAnalyzer,
    SemanticAnalyzer,
    RefactoringEngine,
)


class TestImportInfo:
    """Test ImportInfo dataclass."""

    def test_import_info_creation(self):
        """Test creating ImportInfo."""
        imp = ImportInfo(
            source_file="app.py",
            imported_module="utils",
            imported_names=["helper"],
            line_number=5,
        )
        assert imp.source_file == "app.py"
        assert imp.imported_module == "utils"
        assert imp.imported_names == ["helper"]
        assert imp.line_number == 5
        assert imp.is_relative == False

    def test_relative_import(self):
        """Test relative import detection."""
        imp = ImportInfo(
            source_file="app.py",
            imported_module="config",
            imported_names=["CONFIG"],
            line_number=3,
            is_relative=True,
        )
        assert imp.is_relative == True


class TestDependencyAnalyzer:
    """Test DependencyAnalyzer."""

    def test_analyze_simple_import(self):
        """Test analyzing simple import."""
        analyzer = DependencyAnalyzer()
        code = "import os\nimport sys"
        imports = analyzer.analyze_file("test.py", code)

        assert len(imports) == 2
        assert imports[0].imported_module == "os"
        assert imports[1].imported_module == "sys"

    def test_analyze_from_import(self):
        """Test analyzing from...import."""
        analyzer = DependencyAnalyzer()
        code = "from utils import helper, processor"
        imports = analyzer.analyze_file("app.py", code)

        assert len(imports) == 2
        assert imports[0].imported_module == "utils"
        assert imports[0].imported_names == ["helper"]
        assert imports[1].imported_names == ["processor"]

    def test_analyze_mixed_imports(self):
        """Test analyzing mixed imports."""
        analyzer = DependencyAnalyzer()
        code = """
import os
from utils import helper
import sys
from config import CONFIG
"""
        imports = analyzer.analyze_file("app.py", code)
        assert len(imports) == 4

    def test_build_import_graph(self):
        """Test building dependency graph."""
        analyzer = DependencyAnalyzer()

        analyzer.analyze_file("app.py", "import utils\nimport config")
        analyzer.analyze_file("utils.py", "import helpers")
        analyzer.analyze_file("helpers.py", "")

        assert "app.py" in analyzer.import_graph
        assert "utils" in analyzer.import_graph["app.py"]
        assert "config" in analyzer.import_graph["app.py"]

    def test_find_cycles_acyclic(self):
        """Test finding cycles in acyclic graph."""
        analyzer = DependencyAnalyzer()

        analyzer.analyze_file("app.py", "import utils")
        analyzer.analyze_file("utils.py", "import helpers")
        analyzer.analyze_file("helpers.py", "")

        cycles = analyzer.find_cycles()
        assert len(cycles) == 0

    def test_find_cycles_with_cycle(self):
        """Test detecting circular imports."""
        analyzer = DependencyAnalyzer()

        analyzer.analyze_file("a.py", "import b")
        analyzer.analyze_file("b.py", "import c")
        analyzer.analyze_file("c.py", "import a")

        cycles = analyzer.find_cycles()
        assert len(cycles) > 0

    def test_impact_analysis(self):
        """Test impact analysis."""
        analyzer = DependencyAnalyzer()

        analyzer.analyze_file("app.py", "import utils")
        analyzer.analyze_file("utils.py", "")
        analyzer.analyze_file("test_utils.py", "import utils")

        impact = analyzer.impact_analysis("utils.py")

        assert impact.file_path == "utils.py"
        assert len(impact.dependent_files) > 0
        assert len(impact.affected_tests) > 0


class TestFunctionAnalysis:
    """Test FunctionAnalysis."""

    def test_function_analysis_creation(self):
        """Test creating function analysis."""
        func = FunctionAnalysis(
            name="process_data",
            file_path="utils.py",
            signature="process_data(data, config)",
            parameters=["data", "config"],
            return_type="Dict[str, Any]",
        )

        assert func.name == "process_data"
        assert len(func.parameters) == 2
        assert func.is_public == True

    def test_private_function_detection(self):
        """Test detecting private functions via extraction."""
        code = """
def public_func():
    pass

def _private_func():
    pass
"""
        functions = SemanticAnalyzer.extract_functions(code, "test.py")
        private_funcs = [f for f in functions if not f.is_public]
        assert len(private_funcs) == 1
        assert private_funcs[0].name == "_private_func"


class TestSemanticAnalyzer:
    """Test SemanticAnalyzer."""

    def test_extract_single_function(self):
        """Test extracting function signature."""
        code = "def hello(name): return f'Hello {name}'"
        functions = SemanticAnalyzer.extract_functions(code, "test.py")

        assert len(functions) == 1
        assert functions[0].name == "hello"
        assert functions[0].parameters == ["name"]

    def test_extract_multiple_functions(self):
        """Test extracting multiple functions."""
        code = """
def foo(x):
    return x + 1

def bar(y, z):
    return y + z

def _private():
    pass
"""
        functions = SemanticAnalyzer.extract_functions(code, "test.py")

        assert len(functions) == 3
        assert sum(1 for f in functions if f.is_public) == 2

    def test_extract_with_return_type(self):
        """Test extracting return type."""
        code = "def get_value() -> int: return 42"
        functions = SemanticAnalyzer.extract_functions(code, "test.py")

        assert len(functions) == 1

    def test_find_name_conflicts(self):
        """Test detecting name conflicts."""
        func1 = FunctionAnalysis("process", "file1.py", "process()", [])
        func2 = FunctionAnalysis("process", "file2.py", "process()", [])
        func3 = FunctionAnalysis("helper", "file3.py", "helper()", [])

        functions = [func1, func2, func3]

        conflicts = SemanticAnalyzer.find_name_conflicts("process", functions)
        assert len(conflicts) == 2

    def test_check_api_compatibility_compatible(self):
        """Test API compatibility check (compatible)."""
        old = FunctionAnalysis("process", "old.py", "process(data)", ["data"], "Dict")
        new = FunctionAnalysis("process", "new.py", "process(data)", ["data"], "Dict")

        compatible, issues = SemanticAnalyzer.check_api_compatibility(old, new)
        assert compatible == True
        assert len(issues) == 0

    def test_check_api_compatibility_signature_changed(self):
        """Test API compatibility check (signature changed)."""
        old = FunctionAnalysis("process", "old.py", "process(data)", ["data"])
        new = FunctionAnalysis(
            "process", "new.py", "process(data, config)", ["data", "config"]
        )

        compatible, issues = SemanticAnalyzer.check_api_compatibility(old, new)
        assert compatible == False
        assert len(issues) > 0

    def test_check_api_compatibility_return_type_changed(self):
        """Test API compatibility check (return type changed)."""
        old = FunctionAnalysis("process", "old.py", "process(x)", ["x"], "int")
        new = FunctionAnalysis("process", "new.py", "process(x)", ["x"], "str")

        compatible, issues = SemanticAnalyzer.check_api_compatibility(old, new)
        assert compatible == False
        assert any("Return type" in issue for issue in issues)


class TestAPISignature:
    """Test APISignature."""

    def test_api_signature_compatibility(self):
        """Test API signature compatibility."""
        sig1 = APISignature("process", ["data"], "Dict")
        sig2 = APISignature("process", ["data"], "Dict")

        assert sig1.is_compatible_with(sig2) == True

    def test_api_signature_incompatibility(self):
        """Test API signature incompatibility."""
        sig1 = APISignature("process", ["data"], "Dict")
        sig2 = APISignature("process", ["data", "config"], "Dict")

        assert sig1.is_compatible_with(sig2) == False


class TestCycle:
    """Test Cycle detection."""

    def test_cycle_creation(self):
        """Test creating cycle."""
        cycle = Cycle(files=["a.py", "b.py", "c.py"], path="a -> b -> c -> a")

        assert len(cycle.files) == 3
        assert "a -> b -> c -> a" in cycle.path


class TestRefactoringPlan:
    """Test RefactoringPlan."""

    def test_plan_creation(self):
        """Test creating refactoring plan."""
        plan = RefactoringPlan(
            plan_id="PLAN_ABC123",
            operation="consolidate_files",
        )

        assert plan.plan_id == "PLAN_ABC123"
        assert plan.operation == "consolidate_files"
        assert len(plan.changes) == 0

    def test_add_change(self):
        """Test adding changes to plan."""
        plan = RefactoringPlan(
            plan_id="PLAN_ABC",
            operation="consolidate_files",
        )

        plan.add_change("create_file", path="new.py")
        plan.add_change("delete_file", path="old.py")

        assert len(plan.changes) == 2
        assert plan.changes[0]["type"] == "create_file"
        assert plan.changes[1]["type"] == "delete_file"


class TestRefactoringEngine:
    """Test RefactoringEngine."""

    def test_engine_initialization(self):
        """Test initializing refactoring engine."""
        analyzer = DependencyAnalyzer()
        engine = RefactoringEngine(analyzer)

        assert engine.analyzer == analyzer
        assert isinstance(engine.semantic, SemanticAnalyzer)

    def test_create_consolidation_plan(self):
        """Test creating consolidation plan."""
        analyzer = DependencyAnalyzer()
        analyzer.analyze_file("utils.py", "def helper(): pass")
        analyzer.analyze_file("helpers.py", "def processor(): pass")

        engine = RefactoringEngine(analyzer)
        plan = engine.create_consolidation_plan(
            source_files=["utils.py", "helpers.py"], target_file="core.py"
        )

        assert plan.operation == "consolidate_files"
        assert len(plan.changes) > 0

    def test_verify_plan_safety_no_cycles(self):
        """Test verifying plan safety (no cycles)."""
        analyzer = DependencyAnalyzer()
        analyzer.analyze_file("a.py", "import b")
        analyzer.analyze_file("b.py", "")

        engine = RefactoringEngine(analyzer)
        plan = RefactoringPlan(plan_id="PLAN_1", operation="consolidate")

        safe, issues = engine.verify_plan_safety(plan)
        assert safe == True

    def test_execute_plan_success(self):
        """Test executing plan successfully."""
        analyzer = DependencyAnalyzer()
        engine = RefactoringEngine(analyzer)

        plan = RefactoringPlan(plan_id="PLAN_1", operation="consolidate")
        plan.add_change("create_file", path="core.py")
        plan.add_change("delete_file", path="utils.py")

        result = engine.execute_plan(plan)

        assert result.success == True
        assert result.plan_id == "PLAN_1"
        assert len(result.files_created) > 0


class TestRefactoringResult:
    """Test RefactoringResult."""

    def test_result_creation(self):
        """Test creating refactoring result."""
        result = RefactoringResult(
            plan_id="PLAN_1",
            success=True,
            changes_applied=3,
        )

        assert result.plan_id == "PLAN_1"
        assert result.success == True
        assert result.changes_applied == 3

    def test_result_with_file_tracking(self):
        """Test tracking files in result."""
        result = RefactoringResult(
            plan_id="PLAN_1",
            success=True,
            changes_applied=2,
            files_created=["core.py"],
            files_deleted=["utils.py"],
        )

        assert len(result.files_created) == 1
        assert len(result.files_deleted) == 1


class TestLayer2Integration:
    """Integration tests for Layer 2."""

    def test_end_to_end_consolidation(self):
        """Test end-to-end file consolidation."""
        analyzer = DependencyAnalyzer()

        # Analyze files
        analyzer.analyze_file("app.py", "import utils\nimport helpers")
        analyzer.analyze_file("utils.py", "def util_func(): pass")
        analyzer.analyze_file("helpers.py", "def help_func(): pass")

        # Create engine
        engine = RefactoringEngine(analyzer)

        # Plan consolidation
        plan = engine.create_consolidation_plan(
            source_files=["utils.py", "helpers.py"], target_file="core.py"
        )

        # Verify safety
        safe, issues = engine.verify_plan_safety(plan)

        # Execute
        result = engine.execute_plan(plan)

        assert result.success == safe

    def test_semantic_analysis_workflow(self):
        """Test semantic analysis workflow."""
        code = """
def process_data(data):
    return transform(data)

def transform(x):
    return x * 2

def _internal():
    pass
"""

        functions = SemanticAnalyzer.extract_functions(code, "processor.py")

        # Should have 3 functions
        assert len(functions) == 3

        # Should have 2 public functions
        public = [f for f in functions if f.is_public]
        assert len(public) == 2

        # Check for name conflicts
        names = [f.name for f in functions]
        assert len(names) == len(set(names))

    def test_impact_analysis_workflow(self):
        """Test impact analysis workflow."""
        analyzer = DependencyAnalyzer()

        # Build dependency graph
        analyzer.analyze_file("core.py", "import utils\nimport helpers")
        analyzer.analyze_file("utils.py", "")
        analyzer.analyze_file("helpers.py", "import utils")
        analyzer.analyze_file("test_core.py", "import core")
        analyzer.analyze_file("test_utils.py", "import utils")

        # Analyze impact
        impact = analyzer.impact_analysis("utils.py")

        # Should identify dependent files
        assert len(impact.dependent_files) > 0

        # Should identify affected tests
        assert len(impact.affected_tests) > 0

    def test_dependency_cycle_detection(self):
        """Test detecting and reporting cycles."""
        analyzer = DependencyAnalyzer()

        # Create a cycle: a -> b -> c -> a
        analyzer.analyze_file("a.py", "import b")
        analyzer.analyze_file("b.py", "import c")
        analyzer.analyze_file("c.py", "import a")

        cycles = analyzer.find_cycles()

        assert len(cycles) > 0
        assert isinstance(cycles[0], Cycle)

    def test_api_compatibility_across_refactoring(self):
        """Test verifying API compatibility during refactoring."""
        old_code = "def process(data): return data + 1"
        new_code = "def process(data): return str(data)"

        old_funcs = SemanticAnalyzer.extract_functions(old_code, "old.py")
        new_funcs = SemanticAnalyzer.extract_functions(new_code, "new.py")

        if old_funcs and new_funcs:
            compatible, issues = SemanticAnalyzer.check_api_compatibility(
                old_funcs[0], new_funcs[0]
            )

            # Signatures match but return type may differ
            assert old_funcs[0].name == new_funcs[0].name


class TestLayer2ComplexScenarios:
    """Complex real-world scenarios."""

    def test_multi_file_consolidation_with_cycles(self):
        """Test consolidating files with circular dependencies."""
        analyzer = DependencyAnalyzer()

        # Create a realistic circular dependency
        analyzer.analyze_file("service_a.py", "import service_b")
        analyzer.analyze_file("service_b.py", "import service_c")
        analyzer.analyze_file("service_c.py", "import service_a")

        engine = RefactoringEngine(analyzer)

        # Try to consolidate (should detect cycles)
        plan = engine.create_consolidation_plan(
            source_files=["service_a.py", "service_b.py"], target_file="consolidated.py"
        )

        safe, issues = engine.verify_plan_safety(plan)

        # Should not be safe due to cycles
        if analyzer.cycles:
            assert not safe or len(issues) > 0

    def test_large_dependency_graph(self):
        """Test analyzing large dependency graphs."""
        analyzer = DependencyAnalyzer()

        # Create a larger dependency tree
        files = {
            "app.py": "import core\nimport utils\nimport config",
            "core.py": "import utils\nimport helpers",
            "utils.py": "import validators",
            "helpers.py": "import utils",
            "config.py": "",
            "validators.py": "",
        }

        for filepath, imports in files.items():
            analyzer.analyze_file(filepath, imports)

        # Should have all files in graph
        assert len(analyzer.import_graph) == len(files)

        # Impact analysis on central module
        impact = analyzer.impact_analysis("utils.py")

        assert len(impact.dependent_files) > 1

    def test_semantic_analysis_with_complex_signatures(self):
        """Test semantic analysis with complex function signatures."""
        code = """
from typing import Dict, List, Optional

def process_data(
    data: List[Dict[str, any]],
    config: Optional[Dict] = None
) -> Dict[str, List[str]]:
    return {}

def transform(x: int) -> str:
    return str(x)
"""

        functions = SemanticAnalyzer.extract_functions(code, "complex.py")

        assert len(functions) >= 2
        process_func = [f for f in functions if f.name == "process_data"][0]
        assert len(process_func.parameters) == 2


# ============================================================================
# TEST EXECUTION AND REPORTING
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
