"""
Parse requirements from project markdown files into structured data.
"""

import re
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class FunctionalRequirement:
    req_id: str
    title: str
    category: str
    priority: str
    actor: str
    use_case: str
    acceptance_criteria: List[Dict[str, str]]
    test_cases: List[str]
    components: List[str]

@dataclass
class NonFunctionalRequirement:
    req_id: str
    category: str
    title: str
    specification: str
    measurement_method: str
    target: str
    alert_threshold: str
    test_case: str
    rationale: str

def parse_functional_requirements(content: str) -> List[FunctionalRequirement]:
    """Parse FUNCTIONAL_REQUIREMENTS.md and extract FR-XXX entries."""

    requirements = []

    # Split by ## FR-XXX: Title format
    fr_pattern = r'## (FR-\d+):\s*(.+?)(?=\n---\n|## FR-\d+|$)'
    fr_blocks = re.findall(fr_pattern, content, re.DOTALL)

    for req_id, block in fr_blocks:
        try:
            req = parse_fr_block(req_id, block)
            if req:
                requirements.append(req)
        except Exception as e:
            print(f"Error parsing {req_id}: {e}")
            continue

    return requirements

def parse_fr_block(req_id: str, block: str) -> FunctionalRequirement:
    """Parse a single FR block."""

    lines = block.split('\n')

    # Title is the first line (comes from header)
    title = lines[0].strip() if lines else ""

    # Extract actor from **Actor:** field
    actor_match = re.search(r'\*\*Actor:\*\*\s*(.+?)(?:\n|$)', block)
    actor = actor_match.group(1).strip() if actor_match else ""

    # Extract use case from **Use Case:** field
    use_case_match = re.search(r'\*\*Use Case:\*\*\s*(.*?)(?=\*\*Acceptance|$)', block, re.DOTALL)
    use_case = use_case_match.group(1).strip() if use_case_match else ""

    # Extract acceptance criteria (bullet list items)
    acceptance_criteria = []
    criteria_section = re.search(r'\*\*Acceptance Criteria:\*\*(.*?)(?=\*\*Test Cases:|$)', block, re.DOTALL)
    if criteria_section:
        criteria_lines = criteria_section.group(1).strip().split('\n')
        for line in criteria_lines:
            line = line.strip()
            if line.startswith('- '):
                criteria_text = line[2:].strip()
                acceptance_criteria.append({
                    "id": f"CR-{len(acceptance_criteria)+1:03d}",
                    "description": criteria_text
                })

    # Extract test cases (bullet list items)
    test_cases = []
    test_section = re.search(r'\*\*Test Cases:\*\*(.*?)(?=$)', block, re.DOTALL)
    if test_section:
        test_lines = test_section.group(1).strip().split('\n')
        for line in test_lines:
            line = line.strip()
            if line.startswith('- '):
                # Extract test name, removing backticks if present
                test_name = line[2:].strip()
                test_name = test_name.strip('`')
                test_cases.append(test_name)

    return FunctionalRequirement(
        req_id=req_id,
        title=title,
        category="",
        priority="",
        actor=actor,
        use_case=use_case,
        acceptance_criteria=acceptance_criteria,
        test_cases=test_cases,
        components=[]
    )

def parse_nonfunctional_requirements(content: str) -> List[NonFunctionalRequirement]:
    """Parse NONFUNCTIONAL_REQUIREMENTS.md and extract NFR-XXX entries."""

    requirements = []

    # Split by ## NFR-XXX: Title format
    nfr_pattern = r'## (NFR-\d+):\s*(.+?)(?=\n---\n|## NFR-\d+|$)'
    nfr_blocks = re.findall(nfr_pattern, content, re.DOTALL)

    for req_id, block in nfr_blocks:
        try:
            req = parse_nfr_block(req_id, block)
            if req:
                requirements.append(req)
        except Exception as e:
            print(f"Error parsing {req_id}: {e}")
            continue

    return requirements

def parse_nfr_block(req_id: str, block: str) -> NonFunctionalRequirement:
    """Parse a single NFR block."""

    lines = block.split('\n')

    # Title is the first line (comes from header)
    title = lines[0].strip() if lines else ""

    # Extract category from **Category:** field
    category_match = re.search(r'\*\*Category:\*\*\s*(.+?)(?:\n|$)', block)
    category = category_match.group(1).strip() if category_match else ""

    # Extract specification from **Specification:** field
    spec_match = re.search(r'\*\*Specification:\*\*\s*(.*?)(?=\*\*Target:|Measure via:|$)', block, re.DOTALL)
    specification = spec_match.group(1).strip() if spec_match else ""

    # Extract target from **Target:** field (can be multi-line)
    target_match = re.search(r'\*\*Target:\*\*\s*(.*?)(?=\*\*Current:|Measure via:|$)', block, re.DOTALL)
    target = target_match.group(1).strip() if target_match else ""

    # Extract measurement method from "Measure via:" line
    measurement_match = re.search(r'Measure via:\s*(.*?)(?=\n|Alert when:|$)', block)
    measurement_method = measurement_match.group(1).strip() if measurement_match else ""

    # Extract alert threshold from "Alert when:" line
    alert_match = re.search(r'Alert when:\s*(.*?)(?=\n|Health check:|$)', block)
    alert_threshold = alert_match.group(1).strip() if alert_match else ""

    return NonFunctionalRequirement(
        req_id=req_id,
        category=category,
        title=title,
        specification=specification,
        measurement_method=measurement_method,
        target=target,
        alert_threshold=alert_threshold,
        test_case="",
        rationale=""
    )

def load_and_parse_project_requirements(project_path: str) -> Dict[str, Any]:
    """Load and parse all requirements from a project directory."""

    from pathlib import Path

    project_dir = Path(project_path)
    result = {
        "functional": [],
        "nonfunctional": [],
        "errors": []
    }

    # Try functional requirements (check multiple locations)
    func_req_paths = [
        project_dir / "FUNCTIONAL_REQUIREMENTS.md",
        project_dir / "requirements" / "FUNCTIONAL_REQUIREMENTS.md",
    ]
    for func_req_path in func_req_paths:
        if func_req_path.exists():
            try:
                content = func_req_path.read_text()
                result["functional"] = parse_functional_requirements(content)
                break
            except Exception as e:
                result["errors"].append(f"Failed to parse {func_req_path}: {e}")

    # Try nonfunctional requirements (check multiple locations)
    nonfunc_req_paths = [
        project_dir / "NONFUNCTIONAL_REQUIREMENTS.md",
        project_dir / "requirements" / "NONFUNCTIONAL_REQUIREMENTS.md",
    ]
    for nonfunc_req_path in nonfunc_req_paths:
        if nonfunc_req_path.exists():
            try:
                content = nonfunc_req_path.read_text()
                result["nonfunctional"] = parse_nonfunctional_requirements(content)
                break
            except Exception as e:
                result["errors"].append(f"Failed to parse {nonfunc_req_path}: {e}")

    return result
