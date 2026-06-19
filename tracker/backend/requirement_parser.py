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

    # Split by FR-XXX headers
    fr_pattern = r'## (FR-\d+):\s*(.+?)(?=## FR-\d+|$)'
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

    # Extract metadata
    title_match = re.search(r'\*\*Title:\*\*\s*(.+?)(?:\n|$)', block)
    title = title_match.group(1).strip() if title_match else ""

    category_match = re.search(r'\*\*Category:\*\*\s*(.+?)(?:\n|$)', block)
    category = category_match.group(1).strip() if category_match else ""

    priority_match = re.search(r'\*\*Priority:\*\*\s*(.+?)(?:\n|$)', block)
    priority = priority_match.group(1).strip() if priority_match else ""

    actor_match = re.search(r'\*\*Actor:\*\*\s*(.+?)(?:\n|$)', block)
    actor = actor_match.group(1).strip() if actor_match else ""

    # Extract use case flow
    use_case_match = re.search(r'### Use Case Flow\s*(.*?)(?=###|$)', block, re.DOTALL)
    use_case = use_case_match.group(1).strip() if use_case_match else ""

    # Extract acceptance criteria
    acceptance_criteria = []
    criteria_pattern = r'- \*\*(CR-\d+)\*?:\s*(.+?)(?=\n-|$)'
    criteria_matches = re.findall(criteria_pattern, block)
    for crit_id, crit_desc in criteria_matches:
        acceptance_criteria.append({
            "id": crit_id,
            "description": crit_desc.strip()
        })

    # Extract test cases
    test_cases = []
    test_pattern = r'- \*\*(?:Unit|Integration|Plausibility)\*?:\s*`([^`]+)`'
    test_matches = re.findall(test_pattern, block)
    test_cases.extend(test_matches)

    # Extract components
    components = []
    components_match = re.search(r'### Related Components\s*(.*?)(?=###|$)', block, re.DOTALL)
    if components_match:
        comp_pattern = r'- `([^`]+)`'
        comp_matches = re.findall(comp_pattern, components_match.group(1))
        components.extend(comp_matches)

    return FunctionalRequirement(
        req_id=req_id,
        title=title,
        category=category,
        priority=priority,
        actor=actor,
        use_case=use_case,
        acceptance_criteria=acceptance_criteria,
        test_cases=test_cases,
        components=components
    )

def parse_nonfunctional_requirements(content: str) -> List[NonFunctionalRequirement]:
    """Parse NONFUNCTIONAL_REQUIREMENTS.md and extract NFR-XXX entries."""

    requirements = []

    # Split by NFR-XXX headers
    nfr_pattern = r'## (NFR-\d+):\s*(.+?)(?=## NFR-\d+|$)'
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

    # Extract metadata
    category_match = re.search(r'\*\*Category:\*\*\s*(.+?)(?:\n|$)', block)
    category = category_match.group(1).strip() if category_match else ""

    title_match = re.search(r'\*\*Title:\*\*\s*(.+?)(?:\n|$)', block)
    title = title_match.group(1).strip() if title_match else ""

    spec_match = re.search(r'\*\*Requirement:\*\*\s*(.*?)(?=\*\*Measurement|###|$)', block, re.DOTALL)
    specification = spec_match.group(1).strip() if spec_match else ""

    measurement_match = re.search(r'\*\*Measurement Method:\*\*\s*(.*?)(?=\*\*Target|###|$)', block, re.DOTALL)
    measurement_method = measurement_match.group(1).strip() if measurement_match else ""

    target_match = re.search(r'\*\*Target:\*\*\s*(.*?)(?=\*\*Alert|###|$)', block, re.DOTALL)
    target = target_match.group(1).strip() if target_match else ""

    alert_match = re.search(r'\*\*Alert Threshold:\*\*\s*(.*?)(?=\*\*Test|###|$)', block, re.DOTALL)
    alert_threshold = alert_match.group(1).strip() if alert_match else ""

    test_match = re.search(r'\*\*Test Case:\*\*\s*`?([^`\n]+)`?', block)
    test_case = test_match.group(1).strip() if test_match else ""

    rationale_match = re.search(r'### Rationale\s*(.*?)(?=###|$)', block, re.DOTALL)
    rationale = rationale_match.group(1).strip() if rationale_match else ""

    return NonFunctionalRequirement(
        req_id=req_id,
        category=category,
        title=title,
        specification=specification,
        measurement_method=measurement_method,
        target=target,
        alert_threshold=alert_threshold,
        test_case=test_case,
        rationale=rationale
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

    # Try functional requirements
    func_req_path = project_dir / "requirements" / "FUNCTIONAL_REQUIREMENTS.md"
    if func_req_path.exists():
        try:
            content = func_req_path.read_text()
            result["functional"] = parse_functional_requirements(content)
        except Exception as e:
            result["errors"].append(f"Failed to parse {func_req_path}: {e}")

    # Try nonfunctional requirements
    nonfunc_req_path = project_dir / "NONFUNCTIONAL_REQUIREMENTS.md"
    if nonfunc_req_path.exists():
        try:
            content = nonfunc_req_path.read_text()
            result["nonfunctional"] = parse_nonfunctional_requirements(content)
        except Exception as e:
            result["errors"].append(f"Failed to parse {nonfunc_req_path}: {e}")

    return result
