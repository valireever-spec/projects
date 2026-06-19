"""
Link bugs/gaps to requirements they violate.
Provides traceability from bug → requirement → acceptance criteria → test case.
"""

import json
from typing import Dict, List, Optional, Tuple


class RequirementLinker:
    """Links gaps/bugs to specific requirements and acceptance criteria."""

    @staticmethod
    def suggest_requirements(gap_title: str, gap_description: str, requirements: List[Dict]) -> List[Dict]:
        """
        Suggest requirements that might be violated by this gap.
        Uses keyword matching on requirement titles and descriptions.
        """
        suggestions = []
        gap_text = f"{gap_title} {gap_description}".lower()

        for req in requirements:
            req_text = f"{req['title']} {req.get('description', '')}".lower()

            # Calculate simple keyword overlap score
            gap_words = set(gap_text.split())
            req_words = set(req_text.split())
            overlap = len(gap_words & req_words)

            if overlap > 2:  # At least 3 keyword matches
                suggestions.append({
                    "id": req["id"],
                    "req_id": req["req_id"],
                    "title": req["title"],
                    "req_type": req["req_type"],
                    "category": req["category"],
                    "score": overlap
                })

        # Sort by score descending
        suggestions.sort(key=lambda x: x["score"], reverse=True)
        return suggestions[:5]  # Return top 5 suggestions

    @staticmethod
    def get_acceptance_criteria_for_requirement(requirement: Dict) -> List[Dict]:
        """Extract acceptance criteria from a requirement."""
        criteria = requirement.get("acceptance_criteria", [])

        if not criteria:
            return []

        if isinstance(criteria, str):
            try:
                criteria = json.loads(criteria)
            except:
                return []

        result = []
        for c in criteria:
            if isinstance(c, dict):
                result.append({
                    "id": c.get("id", ""),
                    "description": c.get("description", "")
                })
            elif isinstance(c, str):
                result.append({
                    "id": "",
                    "description": c
                })

        return result

    @staticmethod
    def get_test_cases_for_requirement(requirement: Dict) -> List[str]:
        """Extract test cases from a requirement."""
        tests = requirement.get("test_case", [])

        if not tests:
            return []

        if isinstance(tests, str):
            try:
                tests = json.loads(tests)
            except:
                return [tests]

        return tests if isinstance(tests, list) else [str(tests)]

    @staticmethod
    def build_traceability_chain(gap: Dict, requirement: Dict) -> Dict:
        """Build complete traceability chain: Gap → Requirement → Acceptance Criteria → Tests."""
        criteria = RequirementLinker.get_acceptance_criteria_for_requirement(requirement)
        tests = RequirementLinker.get_test_cases_for_requirement(requirement)

        return {
            "bug": {
                "id": gap.get("id"),
                "title": gap.get("title"),
                "description": gap.get("description"),
                "severity": gap.get("severity"),
                "status": gap.get("status")
            },
            "requirement": {
                "id": requirement.get("id"),
                "req_id": requirement.get("req_id"),
                "title": requirement.get("title"),
                "req_type": requirement.get("req_type"),
                "status": requirement.get("status")
            },
            "acceptance_criteria": criteria,
            "test_cases": tests,
            "chain_summary": f"Bug '{gap.get('title')}' violates {requirement.get('req_id')} ({criteria.__len__()} acceptance criteria, {tests.__len__()} test cases)"
        }

    @staticmethod
    def analyze_requirement_health(requirement: Dict, related_gaps: List[Dict]) -> Dict:
        """Analyze health of a requirement based on related gaps."""
        criteria = RequirementLinker.get_acceptance_criteria_for_requirement(requirement)
        tests = RequirementLinker.get_test_cases_for_requirement(requirement)

        health_status = "Healthy"
        if len(related_gaps) > 0:
            health_status = "At Risk"
        if requirement.get("status") != "Validated":
            health_status = "Unvalidated"

        return {
            "req_id": requirement.get("req_id"),
            "title": requirement.get("title"),
            "status": requirement.get("status"),
            "health": health_status,
            "gap_count": len(related_gaps),
            "criteria_count": len(criteria),
            "test_count": len(tests),
            "risk_level": "Critical" if len(related_gaps) >= 3 else "High" if len(related_gaps) >= 1 else "Low"
        }
